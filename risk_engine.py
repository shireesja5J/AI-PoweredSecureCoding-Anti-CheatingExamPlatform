"""
AI Proctoring Service - Risk Scoring Engine
Combines face detection, eye tracking, and head pose for comprehensive risk assessment
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
from collections import deque
import time

@dataclass
class RiskFactors:
    face_not_detected: float = 0.0
    multiple_faces: float = 0.0
    looking_away: float = 0.0
    eyes_closed: float = 0.0
    rapid_movement: float = 0.0

@dataclass
class RiskAssessment:
    total_risk: float  # 0-100
    risk_level: str  # 'low', 'medium', 'high', 'critical'
    risk_factors: RiskFactors
    violations_detected: List[str]
    recommendation: str

class RiskEngine:
    def __init__(self, window_size=30):
        self.window_size = window_size
        self.face_history = deque(maxlen=window_size)
        self.gaze_history = deque(maxlen=window_size)
        self.last_face_position = None
        self.last_timestamp = None
        
        # Risk thresholds
        self.RISK_LOW = 30
        self.RISK_MEDIUM = 50
        self.RISK_HIGH = 70
        self.RISK_CRITICAL = 85
        
        # Violation tracking
        self.violation_counts = {
            'face_not_detected': 0,
            'multiple_faces': 0,
            'looking_away': 0,
            'eyes_closed': 0
        }
        
    def analyze_frame(self, 
                     face_detected: bool,
                     multiple_faces: bool,
                     face_count: int,
                     face_location: Optional[tuple],
                     looking_away: bool,
                     eyes_detected: bool,
                     left_eye_open: bool,
                     right_eye_open: bool,
                     gaze_score: float) -> RiskAssessment:
        """Analyze a single frame and calculate risk"""
        
        timestamp = time.time()
        risk_factors = RiskFactors()
        violations = []
        
        # Face detection risk
        if not face_detected:
            risk_factors.face_not_detected = 25.0
            self.violation_counts['face_not_detected'] += 1
            if self.violation_counts['face_not_detected'] > 5:
                violations.append('Face not detected for extended period')
        
        if multiple_faces:
            risk_factors.multiple_faces = 50.0
            self.violation_counts['multiple_faces'] += 1
            violations.append(f'Multiple faces detected ({face_count} faces)')
        
        # Eye/gaze risk
        if looking_away:
            risk_factors.looking_away = min(20.0, gaze_score * 30)
            self.violation_counts['looking_away'] += 1
            if self.violation_counts['looking_away'] > 10:
                violations.append('Frequent looking away detected')
        
        if not left_eye_open and not right_eye_open and eyes_detected:
            risk_factors.eyes_closed = 15.0
            self.violation_counts['eyes_closed'] += 1
        
        # Rapid movement detection
        if face_location and self.last_face_position:
            movement = self._calculate_movement(face_location, self.last_face_position, timestamp)
            if movement > 50:  # Threshold for rapid movement
                risk_factors.rapid_movement = 10.0
                violations.append('Rapid head movement detected')
        
        # Update history
        self.face_history.append((face_detected, multiple_faces, face_location))
        self.gaze_history.append((looking_away, gaze_score))
        self.last_face_position = face_location
        self.last_timestamp = timestamp
        
        # Calculate total risk
        base_risk = sum([
            risk_factors.face_not_detected,
            risk_factors.multiple_faces,
            risk_factors.looking_away,
            risk_factors.eyes_closed,
            risk_factors.rapid_movement
        ])
        
        # Apply temporal smoothing
        temporal_risk = self._calculate_temporal_risk()
        total_risk = min(100, (base_risk * 0.7) + (temporal_risk * 0.3))
        
        # Determine risk level
        risk_level = self._get_risk_level(total_risk)
        recommendation = self._get_recommendation(total_risk, violations)
        
        return RiskAssessment(
            total_risk=round(total_risk, 1),
            risk_level=risk_level,
            risk_factors=risk_factors,
            violations_detected=violations,
            recommendation=recommendation
        )
    
    def _calculate_movement(self, current_pos, last_pos, timestamp):
        """Calculate movement speed between frames"""
        if self.last_timestamp is None or not current_pos or not last_pos:
            return 0.0
        
        # current_pos and last_pos are tuples: (x, y, width, height)
        # Use center points for comparison
        current_center = (current_pos[0] + current_pos[2]/2, current_pos[1] + current_pos[3]/2)
        last_center = (last_pos[0] + last_pos[2]/2, last_pos[1] + last_pos[3]/2)
        
        dx = current_center[0] - last_center[0]
        dy = current_center[1] - last_center[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        dt = timestamp - self.last_timestamp
        
        if dt > 0:
            return distance / dt
        return 0.0
    
    def _calculate_temporal_risk(self):
        """Calculate risk based on temporal patterns"""
        if len(self.face_history) < 5:
            return 0.0
        
        recent_history = list(self.face_history)[-10:]
        
        # Count consecutive face misses
        face_misses = sum(1 for f, m, l in recent_history if not f)
        
        # Count looking away frequency
        looking_away_count = sum(1 for l, g in list(self.gaze_history)[-10:] if l)
        
        # Calculate temporal risk
        temporal_risk = 0.0
        if face_misses > 3:
            temporal_risk += face_misses * 3
        if looking_away_count > 5:
            temporal_risk += looking_away_count * 2
        
        return min(40, temporal_risk)
    
    def _get_risk_level(self, total_risk: float) -> str:
        """Determine risk level from total risk score"""
        if total_risk >= self.RISK_CRITICAL:
            return 'critical'
        elif total_risk >= self.RISK_HIGH:
            return 'high'
        elif total_risk >= self.RISK_MEDIUM:
            return 'medium'
        elif total_risk >= self.RISK_LOW:
            return 'low'
        return 'minimal'
    
    def _get_recommendation(self, total_risk: float, violations: List[str]) -> str:
        """Generate recommendation based on risk level"""
        if total_risk >= self.RISK_CRITICAL:
            return 'IMMEDIATE_REVIEW: Critical anomalies detected. Auto-submit recommended.'
        elif total_risk >= self.RISK_HIGH:
            return 'HIGH_ALERT: Serious irregularities. Flag for manual review.'
        elif total_risk >= self.RISK_MEDIUM:
            return 'WARNING: Multiple anomalies detected. Monitor closely.'
        elif total_risk >= self.RISK_LOW:
            return 'NOTICE: Minor irregularities. Continue monitoring.'
        return 'NORMAL: Exam proceeding within normal parameters.'
    
    def get_risk_increment(self, current_risk: float) -> int:
        """Calculate risk increment for cheating score"""
        if current_risk > 70:
            return 15
        elif current_risk > 50:
            return 8
        elif current_risk > 30:
            return 4
        return 1
    
    def reset(self):
        """Reset the risk engine state"""
        self.face_history.clear()
        self.gaze_history.clear()
        self.last_face_position = None
        self.last_timestamp = None
        self.violation_counts = {
            'face_not_detected': 0,
            'multiple_faces': 0,
            'looking_away': 0,
            'eyes_closed': 0
        }
