"""
AI Proctoring Service - Main FastAPI Application
Provides endpoints for face detection, eye tracking, and risk assessment
"""

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import cv2
import numpy as np
import base64
import io
from PIL import Image
import logging

from face_detection import FaceDetector, FaceDetectionResult
from eye_tracking import EyeTracker, EyeTrackingResult
from risk_engine import RiskEngine, RiskAssessment

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="AI Proctoring Service",
    description="Real-time AI proctoring with face detection, eye tracking, and risk assessment",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI components
face_detector = FaceDetector(min_detection_confidence=0.5)
eye_tracker = EyeTracker(min_detection_confidence=0.5)
risk_engine = RiskEngine(window_size=30)

# Request/Response Models
class FrameRequest(BaseModel):
    frame: str  # Base64 encoded image
    session_id: Optional[str] = None

class FaceDetectionResponse(BaseModel):
    face_detected: bool
    multiple_faces: bool
    face_count: int
    confidence: float

class EyeTrackingResponse(BaseModel):
    eyes_detected: bool
    looking_away: bool
    eye_direction: str
    gaze_score: float

class RiskScoreResponse(BaseModel):
    total_risk: float
    risk_level: str
    risk_increment: int
    violations: List[str]
    recommendation: str

class ProctoringResponse(BaseModel):
    face_detected: bool
    multiple_faces: bool
    looking_away: bool
    eye_direction: str
    risk_score: float
    risk_level: str
    risk_increment: int
    message: str

def decode_base64_frame(base64_string: str) -> np.ndarray:
    """Decode base64 image to OpenCV format"""
    try:
        # Remove data URI prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64
        img_bytes = base64.b64decode(base64_string)
        img = Image.open(io.BytesIO(img_bytes))
        
        # Convert to OpenCV format (BGR)
        cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        return cv_img
    except Exception as e:
        logger.error(f"Error decoding frame: {e}")
        raise HTTPException(status_code=400, detail="Invalid image format")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "face_detection": "ready",
            "eye_tracking": "ready",
            "risk_engine": "ready"
        }
    }

@app.post("/detect-face", response_model=FaceDetectionResponse)
async def detect_face(request: FrameRequest):
    """Detect faces in the provided frame"""
    try:
        frame = decode_base64_frame(request.frame)
        result = face_detector.detect_faces(frame)
        
        return FaceDetectionResponse(
            face_detected=result.face_detected,
            multiple_faces=result.multiple_faces,
            face_count=result.face_count,
            confidence=result.confidence
        )
    except Exception as e:
        logger.error(f"Face detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/detect-multiple-faces")
async def detect_multiple_faces(request: FrameRequest):
    """Check for multiple faces (cheating indicator)"""
    try:
        frame = decode_base64_frame(request.frame)
        result = face_detector.detect_faces(frame)
        
        return {
            "multiple_faces": result.multiple_faces,
            "face_count": result.face_count,
            "faces": result.face_locations
        }
    except Exception as e:
        logger.error(f"Multiple face detection error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/eye-tracking", response_model=EyeTrackingResponse)
async def eye_tracking(request: FrameRequest):
    """Track eyes and determine gaze direction"""
    try:
        frame = decode_base64_frame(request.frame)
        result = eye_tracker.track_eyes(frame)
        
        return EyeTrackingResponse(
            eyes_detected=result.eyes_detected,
            looking_away=result.looking_away,
            eye_direction=result.eye_direction,
            gaze_score=result.gaze_score
        )
    except Exception as e:
        logger.error(f"Eye tracking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/risk-score", response_model=RiskScoreResponse)
async def risk_score(
    face_detected: bool = Body(...),
    multiple_faces: bool = Body(...),
    face_count: int = Body(...),
    looking_away: bool = Body(...),
    eyes_detected: bool = Body(...),
    left_eye_open: bool = Body(default=True),
    right_eye_open: bool = Body(default=True),
    gaze_score: float = Body(default=0.0)
):
    """Calculate risk score based on proctoring data"""
    try:
        assessment = risk_engine.analyze_frame(
            face_detected=face_detected,
            multiple_faces=multiple_faces,
            face_count=face_count,
            face_location=None,
            looking_away=looking_away,
            eyes_detected=eyes_detected,
            left_eye_open=left_eye_open,
            right_eye_open=right_eye_open,
            gaze_score=gaze_score
        )
        
        risk_increment = risk_engine.get_risk_increment(assessment.total_risk)
        
        return RiskScoreResponse(
            total_risk=assessment.total_risk,
            risk_level=assessment.risk_level,
            risk_increment=risk_increment,
            violations=assessment.violations_detected,
            recommendation=assessment.recommendation
        )
    except Exception as e:
        logger.error(f"Risk score error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-frame", response_model=ProctoringResponse)
async def analyze_frame(request: FrameRequest):
    """Complete frame analysis - face, eyes, and risk in one call"""
    try:
        frame = decode_base64_frame(request.frame)
        
        # Face detection
        face_result = face_detector.detect_faces(frame)
        
        # Eye tracking
        eye_result = eye_tracker.track_eyes(frame)
        
        # Risk assessment
        face_location = face_result.face_locations[0] if face_result.face_locations else None
        
        risk_assessment = risk_engine.analyze_frame(
            face_detected=face_result.face_detected,
            multiple_faces=face_result.multiple_faces,
            face_count=face_result.face_count,
            face_location=face_location,
            looking_away=eye_result.looking_away,
            eyes_detected=eye_result.eyes_detected,
            left_eye_open=eye_result.left_eye_open,
            right_eye_open=eye_result.right_eye_open,
            gaze_score=eye_result.gaze_score
        )
        
        risk_increment = risk_engine.get_risk_increment(risk_assessment.total_risk)
        
        # Generate message
        message = "OK"
        if face_result.multiple_faces:
            message = "Multiple faces detected!"
        elif not face_result.face_detected:
            message = "Face not detected!"
        elif eye_result.looking_away:
            message = "Looking away detected"
        
        return ProctoringResponse(
            face_detected=face_result.face_detected,
            multiple_faces=face_result.multiple_faces,
            looking_away=eye_result.looking_away,
            eye_direction=eye_result.eye_direction,
            risk_score=risk_assessment.total_risk,
            risk_level=risk_assessment.risk_level,
            risk_increment=risk_increment,
            message=message
        )
        
    except Exception as e:
        logger.error(f"Frame analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset-risk")
async def reset_risk_engine():
    """Reset the risk engine state (e.g., for new exam session)"""
    risk_engine.reset()
    return {"status": "reset", "message": "Risk engine state cleared"}

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on shutdown"""
    face_detector.release()
    eye_tracker.release()
    logger.info("AI Proctoring Service shut down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
