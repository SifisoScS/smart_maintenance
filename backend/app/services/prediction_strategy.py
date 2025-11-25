"""
Prediction Strategy Pattern - Zero-Cost Intelligence with AI-Ready Architecture

This module implements the Strategy Pattern for maintenance predictions.
Currently uses rule-based algorithms (zero cost), but architected to easily
swap in ML-based strategies when budget allows.

Author: Sifiso Shezi (ARISAN SIFISO)
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.request import MaintenanceRequest


class PredictionStrategy(ABC):
    """
    Abstract base class for prediction strategies.
    Allows swapping between rule-based and ML-based algorithms.
    """

    @abstractmethod
    def predict_failure(self, asset: Asset, history: List[MaintenanceRequest]) -> Dict:
        """
        Predict when an asset is likely to fail

        Args:
            asset: The asset to analyze
            history: Historical maintenance requests for this asset

        Returns:
            Dict with prediction data:
            {
                'risk_score': float (0-1),
                'predicted_failure_date': datetime,
                'confidence': float (0-1),
                'reasoning': str,
                'recommended_action': str
            }
        """
        pass

    @abstractmethod
    def calculate_health_score(self, asset: Asset, history: List[MaintenanceRequest]) -> float:
        """Calculate overall asset health score (0-100)"""
        pass


class RuleBasedStrategy(PredictionStrategy):
    """
    Rule-Based Prediction Strategy (CURRENT - Zero Cost)

    Uses statistical analysis and pattern recognition:
    - Time between failures (MTBF)
    - Condition degradation patterns
    - Failure frequency analysis
    - Seasonal patterns

    No external AI APIs needed - runs entirely on your infrastructure.
    """

    def __init__(self):
        # Configurable thresholds
        self.high_risk_threshold = 0.75
        self.medium_risk_threshold = 0.50
        self.low_risk_threshold = 0.25

        # Condition score mapping
        self.condition_scores = {
            'excellent': 100,
            'good': 75,
            'fair': 50,
            'poor': 25,
            'critical': 0
        }

    def predict_failure(self, asset: Asset, history: List[MaintenanceRequest]) -> Dict:
        """
        Rule-based failure prediction using statistical analysis
        """
        # Calculate various risk factors
        time_based_risk = self._calculate_time_based_risk(asset, history)
        frequency_risk = self._calculate_frequency_risk(history)
        condition_risk = self._calculate_condition_risk(asset)
        age_risk = self._calculate_age_risk(asset)

        # Weighted average of all risk factors
        risk_score = (
            time_based_risk * 0.35 +
            frequency_risk * 0.25 +
            condition_risk * 0.25 +
            age_risk * 0.15
        )

        # Calculate predicted failure date
        predicted_date = self._calculate_predicted_failure_date(asset, history, risk_score)

        # Determine confidence based on data availability
        confidence = self._calculate_confidence(history)

        # Generate reasoning
        reasoning = self._generate_reasoning(risk_score, time_based_risk, frequency_risk, condition_risk, age_risk)

        # Recommend action
        recommended_action = self._recommend_action(risk_score, predicted_date)

        return {
            'risk_score': round(risk_score, 2),
            'predicted_failure_date': predicted_date,
            'confidence': round(confidence, 2),
            'reasoning': reasoning,
            'recommended_action': recommended_action,
            'risk_factors': {
                'time_based': round(time_based_risk, 2),
                'frequency': round(frequency_risk, 2),
                'condition': round(condition_risk, 2),
                'age': round(age_risk, 2)
            }
        }

    def calculate_health_score(self, asset: Asset, history: List[MaintenanceRequest]) -> float:
        """
        Calculate overall asset health score (0-100)
        """
        # Base score from current condition
        condition_value = asset.condition.value if hasattr(asset.condition, 'value') else str(asset.condition)
        condition_score = self.condition_scores.get(condition_value.lower(), 50)

        # Adjust based on recent maintenance frequency
        if len(history) >= 3:
            recent_requests = sorted(history, key=lambda x: x.created_at, reverse=True)[:3]
            recent_timespan = (recent_requests[0].created_at - recent_requests[-1].created_at).days

            if recent_timespan < 30:  # High frequency = poor health
                condition_score *= 0.7
            elif recent_timespan < 90:
                condition_score *= 0.85

        # Adjust based on asset age
        if asset.purchase_date:
            age_years = (datetime.now().date() - asset.purchase_date).days / 365
            if age_years > 10:
                condition_score *= 0.8
            elif age_years > 5:
                condition_score *= 0.9

        return max(0, min(100, condition_score))

    def _calculate_time_based_risk(self, asset: Asset, history: List[MaintenanceRequest]) -> float:
        """
        Calculate risk based on time patterns (Mean Time Between Failures)
        """
        if len(history) < 2:
            return 0.3  # Default low-medium risk with insufficient data

        # Sort by date
        sorted_history = sorted(history, key=lambda x: x.created_at)

        # Calculate time between each maintenance event
        intervals = []
        for i in range(1, len(sorted_history)):
            days_between = (sorted_history[i].created_at - sorted_history[i-1].created_at).days
            intervals.append(days_between)

        if not intervals:
            return 0.3

        # Calculate average interval (MTBF)
        avg_interval = sum(intervals) / len(intervals)

        # Days since last maintenance
        days_since_last = (datetime.now() - sorted_history[-1].created_at).days

        # Risk increases as we approach the average interval
        if avg_interval > 0:
            risk = days_since_last / avg_interval
            return min(1.0, risk)  # Cap at 1.0

        return 0.5

    def _calculate_frequency_risk(self, history: List[MaintenanceRequest]) -> float:
        """
        Calculate risk based on maintenance frequency
        Higher frequency = higher risk
        """
        if not history:
            return 0.2

        # Count requests in last 180 days
        recent_cutoff = datetime.now() - timedelta(days=180)
        recent_requests = [r for r in history if r.created_at >= recent_cutoff]

        # Risk mapping based on frequency
        count = len(recent_requests)
        if count >= 6:  # 6+ requests in 6 months = very high risk
            return 0.9
        elif count >= 4:
            return 0.7
        elif count >= 2:
            return 0.5
        elif count >= 1:
            return 0.3
        else:
            return 0.1

    def _calculate_condition_risk(self, asset: Asset) -> float:
        """
        Calculate risk based on current asset condition
        """
        condition_risk_map = {
            'excellent': 0.1,
            'good': 0.3,
            'fair': 0.6,
            'poor': 0.85,
            'critical': 0.95
        }
        condition_value = asset.condition.value if hasattr(asset.condition, 'value') else str(asset.condition)
        return condition_risk_map.get(condition_value.lower(), 0.5)

    def _calculate_age_risk(self, asset: Asset) -> float:
        """
        Calculate risk based on asset age
        """
        if not asset.purchase_date:
            return 0.3  # Unknown age = moderate risk

        age_years = (datetime.now().date() - asset.purchase_date).days / 365

        # Risk increases with age
        if age_years >= 15:
            return 0.9
        elif age_years >= 10:
            return 0.7
        elif age_years >= 5:
            return 0.5
        elif age_years >= 2:
            return 0.3
        else:
            return 0.1

    def _calculate_predicted_failure_date(self, asset: Asset, history: List[MaintenanceRequest], risk_score: float) -> Optional[datetime]:
        """
        Predict when failure is likely to occur
        """
        if not history:
            # No history - predict based on condition and age
            if risk_score > 0.8:
                return datetime.now() + timedelta(days=7)
            elif risk_score > 0.6:
                return datetime.now() + timedelta(days=30)
            else:
                return datetime.now() + timedelta(days=90)

        # Use MTBF if available
        sorted_history = sorted(history, key=lambda x: x.created_at)
        if len(sorted_history) >= 2:
            intervals = []
            for i in range(1, len(sorted_history)):
                days = (sorted_history[i].created_at - sorted_history[i-1].created_at).days
                intervals.append(days)

            avg_interval = sum(intervals) / len(intervals)
            last_maintenance = sorted_history[-1].created_at

            # Adjust interval based on risk score (higher risk = sooner failure)
            adjusted_interval = avg_interval * (1 - risk_score * 0.5)

            return last_maintenance + timedelta(days=adjusted_interval)

        return datetime.now() + timedelta(days=60)

    def _calculate_confidence(self, history: List[MaintenanceRequest]) -> float:
        """
        Calculate confidence in prediction based on data availability
        More data = higher confidence
        """
        data_points = len(history)

        if data_points >= 10:
            return 0.95
        elif data_points >= 5:
            return 0.85
        elif data_points >= 3:
            return 0.70
        elif data_points >= 1:
            return 0.55
        else:
            return 0.30

    def _generate_reasoning(self, risk_score: float, time_risk: float, freq_risk: float, condition_risk: float, age_risk: float) -> str:
        """
        Generate human-readable reasoning for the prediction
        """
        reasons = []

        if time_risk > 0.7:
            reasons.append("overdue for maintenance based on historical patterns")
        elif time_risk > 0.5:
            reasons.append("approaching typical maintenance interval")

        if freq_risk > 0.7:
            reasons.append("high frequency of recent repairs indicates deteriorating condition")
        elif freq_risk > 0.5:
            reasons.append("moderate repair frequency detected")

        if condition_risk > 0.7:
            reasons.append("current condition assessment shows significant wear")
        elif condition_risk > 0.5:
            reasons.append("condition has degraded from optimal")

        if age_risk > 0.7:
            reasons.append("asset age exceeds typical service life")
        elif age_risk > 0.5:
            reasons.append("asset is approaching end of typical service life")

        if not reasons:
            return "Asset appears to be in good health with low risk indicators"

        return "Risk factors: " + ", ".join(reasons) + "."

    def _recommend_action(self, risk_score: float, predicted_date: Optional[datetime]) -> str:
        """
        Recommend action based on risk score
        """
        if risk_score >= 0.8:
            return "URGENT: Schedule immediate preventive maintenance to avoid failure"
        elif risk_score >= 0.6:
            return "HIGH PRIORITY: Schedule preventive maintenance within 7 days"
        elif risk_score >= 0.4:
            return "MODERATE: Plan preventive maintenance within 30 days"
        else:
            return "LOW RISK: Continue monitoring, routine maintenance sufficient"


class MLBasedStrategy(PredictionStrategy):
    """
    ML-Based Prediction Strategy (FUTURE - When Budget Available)

    Placeholder for future ML integration:
    - Azure ML
    - AWS SageMaker
    - TensorFlow / PyTorch models
    - Time-series forecasting

    Simply swap strategy when ready: engine.set_strategy(MLBasedStrategy())
    """

    def predict_failure(self, asset: Asset, history: List[MaintenanceRequest]) -> Dict:
        """
        Future: Call ML model API for prediction
        For now: Falls back to rule-based
        """
        # TODO: Implement ML API calls when budget available
        # Example:
        # response = ml_api.predict(features)
        # return parse_ml_response(response)

        # Fallback to rule-based for now
        fallback = RuleBasedStrategy()
        return fallback.predict_failure(asset, history)

    def calculate_health_score(self, asset: Asset, history: List[MaintenanceRequest]) -> float:
        """
        Future: ML-based health scoring
        """
        fallback = RuleBasedStrategy()
        return fallback.calculate_health_score(asset, history)
