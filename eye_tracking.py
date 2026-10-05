"""
AI Proctoring Service - Eye Tracking Module
Uses MediaPipe Face Mesh for detailed eye tracking and gaze estimation
"""

import cv2
import mediapipe as mp
import numpy as np
from typing import Tuple, Optional
from dataclasses import dataclass
import math

@dataclass
class EyeTrackingResult:
    eyes_detected: bool
    looking_away: bool
    eye_direction: str  # 'center', 'left', 'right', 'up', 'down'
    left_eye_open: bool
    right_eye_open: bool
    gaze_score: float  # 0-1, higher means more suspicious

class EyeTracker:
    def __init__(self, min_detection_confidence=0.5):
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_detection_confidence
        )
        
        # Eye landmark indices for MediaPipe Face Mesh
        self.LEFT_EYE_INDICES = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161]
        self.RIGHT_EYE_INDICES = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384]
        self.LEFT_IRIS_INDICES = [469, 470, 471, 472]
        self.RIGHT_IRIS_INDICES = [474, 475, 476, 477]
        
        # Previous positions for smoothing
        self.prev_iris_positions = []
        self.max_history = 10
        
    def track_eyes(self, frame: np.ndarray) -> EyeTrackingResult:
        """Track eyes and determine gaze direction"""
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            return EyeTrackingResult(
                eyes_detected=False,
                looking_away=False,
                eye_direction='unknown',
                left_eye_open=False,
                right_eye_open=False,
                gaze_score=0.0
            )
        
        landmarks = results.multi_face_landmarks[0]
        h, w = frame.shape[:2]
        
        # Get eye landmarks
        left_eye_points = self._get_eye_points(landmarks, self.LEFT_EYE_INDICES, w, h)
        right_eye_points = self._get_eye_points(landmarks, self.RIGHT_EYE_INDICES, w, h)
        left_iris_points = self._get_eye_points(landmarks, self.LEFT_IRIS_INDICES, w, h)
        right_iris_points = self._get_eye_points(landmarks, self.RIGHT_IRIS_INDICES, w, h)
        
        # Check if eyes are open
        left_open = self._is_eye_open(left_eye_points)
        right_open = self._is_eye_open(right_eye_points)
        
        # Calculate gaze direction
        gaze_direction, gaze_score = self._calculate_gaze(
            left_eye_points, right_eye_points, 
            left_iris_points, right_iris_points
        )
        
        looking_away = gaze_score > 0.6 or gaze_direction in ['left', 'right', 'up', 'down']
        
        return EyeTrackingResult(
            eyes_detected=True,
            looking_away=looking_away,
            eye_direction=gaze_direction,
            left_eye_open=left_open,
            right_eye_open=right_open,
            gaze_score=gaze_score
        )
    
    def _get_eye_points(self, landmarks, indices, img_w, img_h):
        """Extract eye landmark points"""
        points = []
        for idx in indices:
            x = int(landmarks.landmark[idx].x * img_w)
            y = int(landmarks.landmark[idx].y * img_h)
            points.append((x, y))
        return points
    
    def _is_eye_open(self, eye_points):
        """Determine if eye is open based on aspect ratio"""
        if len(eye_points) < 6:
            return False
        
        # Calculate eye aspect ratio
        height = abs(eye_points[1][1] - eye_points[5][1])
        width = abs(eye_points[0][0] - eye_points[3][0])
        
        if width == 0:
            return False
            
        aspect_ratio = height / width
        return aspect_ratio > 0.2  # Threshold for open eye
    
    def _calculate_gaze(self, left_eye, right_eye, left_iris, right_iris):
        """Calculate gaze direction based on iris position relative to eye center"""
        if not left_eye or not right_eye or not left_iris or not right_iris:
            return 'unknown', 0.0
        
        # Calculate eye centers as numpy arrays
        left_eye_center = np.array([np.mean([p[0] for p in left_eye]), np.mean([p[1] for p in left_eye])])
        right_eye_center = np.array([np.mean([p[0] for p in right_eye]), np.mean([p[1] for p in right_eye])])
        
        # Calculate iris centers as numpy arrays
        left_iris_center = np.array([np.mean([p[0] for p in left_iris]), np.mean([p[1] for p in left_iris])])
        right_iris_center = np.array([np.mean([p[0] for p in right_iris]), np.mean([p[1] for p in right_iris])])
        
        # Calculate relative iris positions
        left_offset = left_iris_center - left_eye_center
        right_offset = right_iris_center - right_eye_center
        
        # Average the offsets
        avg_offset = (left_offset + right_offset) / 2
        
        # Normalize by eye size
        eye_size = np.linalg.norm(np.array(left_eye[0]) - np.array(left_eye[3]))
        if eye_size > 0:
            normalized_offset = avg_offset / eye_size
        else:
            normalized_offset = avg_offset
        
        # Determine direction
        x, y = normalized_offset
        gaze_score = min(1.0, np.sqrt(x*x + y*y))
        
        if abs(x) > abs(y):
            if x > 0.15:
                return 'left', gaze_score
            elif x < -0.15:
                return 'right', gaze_score
        else:
            if y > 0.15:
                return 'up', gaze_score
            elif y < -0.15:
                return 'down', gaze_score
        
        return 'center', gaze_score
    
    def draw_eye_tracking(self, frame: np.ndarray, result: EyeTrackingResult) -> np.ndarray:
        """Draw eye tracking visualization on frame"""
        annotated = frame.copy()
        
        status_text = f"Eyes: {'Open' if (result.left_eye_open or result.right_eye_open) else 'Closed'}"
        direction_text = f"Gaze: {result.eye_direction}"
        
        color = (0, 255, 0) if not result.looking_away else (0, 165, 255)
        
        cv2.putText(annotated, status_text, (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        cv2.putText(annotated, direction_text, (10, 85),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        if result.looking_away:
            cv2.putText(annotated, "LOOKING AWAY!", (10, 110),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        return annotated
    
    def release(self):
        """Release resources"""
        self.face_mesh.close()
