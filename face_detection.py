"""
AI Proctoring Service - Face Detection Module
Uses MediaPipe for real-time face detection and analysis
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class FaceDetectionResult:
    face_detected: bool
    multiple_faces: bool
    face_count: int
    face_locations: List[Tuple[int, int, int, int]]
    confidence: float

class FaceDetector:
    def __init__(self, min_detection_confidence=0.5):
        self.mp_face_detection = mp.solutions.face_detection
        self.face_detection = self.mp_face_detection.FaceDetection(
            min_detection_confidence=min_detection_confidence,
            model_selection=1  # 0=short range, 1=full range
        )
        
    def detect_faces(self, frame: np.ndarray) -> FaceDetectionResult:
        """Detect faces in the given frame"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process the frame
        results = self.face_detection.process(rgb_frame)
        
        face_locations = []
        face_count = 0
        confidence = 0.0
        
        if results.detections:
            face_count = len(results.detections)
            h, w = frame.shape[:2]
            
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                face_locations.append((x, y, width, height))
                confidence = max(confidence, detection.score[0])
        
        return FaceDetectionResult(
            face_detected=face_count > 0,
            multiple_faces=face_count > 1,
            face_count=face_count,
            face_locations=face_locations,
            confidence=confidence
        )
    
    def draw_faces(self, frame: np.ndarray, result: FaceDetectionResult) -> np.ndarray:
        """Draw face detection results on the frame"""
        annotated = frame.copy()
        
        for (x, y, w, h) in result.face_locations:
            color = (0, 255, 0) if result.face_count == 1 else (0, 0, 255)
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
            
            # Draw confidence
            label = f"Face: {result.confidence:.2f}"
            cv2.putText(annotated, label, (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        if result.multiple_faces:
            cv2.putText(annotated, "MULTIPLE FACES DETECTED!", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        return annotated

    def release(self):
        """Release resources"""
        self.face_detection.close()
