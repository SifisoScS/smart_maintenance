"""
Asset Health Analyzer Service - Orchestrates Predictive Maintenance

This service coordinates the prediction strategy with asset and maintenance data
to provide comprehensive health insights and failure predictions.

Author: Sifiso Shezi (ARISAN SIFISO)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.asset import Asset
from app.models.request import MaintenanceRequest
from app.services.prediction_strategy import PredictionStrategy, RuleBasedStrategy


class AssetHealthService:
    """
    Orchestrates predictive maintenance by combining:
    - Asset data
    - Maintenance history
    - Prediction strategies
    - Health scoring algorithms
    """

    def __init__(self, db: Session, strategy: Optional[PredictionStrategy] = None):
        """
        Initialize with database session and prediction strategy

        Args:
            db: SQLAlchemy database session
            strategy: Prediction strategy (defaults to RuleBasedStrategy)
        """
        self.db = db
        self.strategy = strategy or RuleBasedStrategy()

    def set_strategy(self, strategy: PredictionStrategy):
        """
        Swap prediction strategy at runtime (Strategy Pattern)

        Args:
            strategy: New prediction strategy to use
        """
        self.strategy = strategy

    def analyze_asset(self, asset_id: int) -> Dict:
        """
        Perform comprehensive health analysis on a single asset

        Args:
            asset_id: ID of asset to analyze

        Returns:
            Dict containing:
            - asset_info: Basic asset data
            - health_score: Overall health (0-100)
            - prediction: Failure prediction data
            - maintenance_summary: Historical maintenance stats
            - recommendations: Actionable recommendations
        """
        # Fetch asset
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        # Fetch maintenance history
        history = self.db.query(MaintenanceRequest).filter(
            MaintenanceRequest.asset_id == asset_id
        ).order_by(MaintenanceRequest.created_at.desc()).all()

        # Calculate health score
        health_score = self.strategy.calculate_health_score(asset, history)

        # Generate prediction
        prediction = self.strategy.predict_failure(asset, history)

        # Calculate maintenance statistics
        maintenance_summary = self._calculate_maintenance_summary(history)

        # Generate recommendations
        recommendations = self._generate_recommendations(
            asset, health_score, prediction, maintenance_summary
        )

        return {
            'asset_info': {
                'id': asset.id,
                'name': asset.name,
                'asset_tag': asset.asset_tag,
                'category': asset.category.value if hasattr(asset.category, 'value') else str(asset.category),
                'location': asset.full_location,
                'condition': asset.condition.value if hasattr(asset.condition, 'value') else str(asset.condition),
                'status': asset.status.value if hasattr(asset.status, 'value') else str(asset.status),
                'purchase_date': asset.purchase_date
            },
            'health_score': health_score,
            'prediction': prediction,
            'maintenance_summary': maintenance_summary,
            'recommendations': recommendations,
            'analyzed_at': datetime.now()
        }

    def analyze_all_assets(self, organization_id: Optional[int] = None) -> List[Dict]:
        """
        Analyze all assets, optionally filtered by organization

        Args:
            organization_id: Filter by organization (for multi-tenant)

        Returns:
            List of asset health analyses, sorted by risk (highest first)
        """
        # Build query
        query = self.db.query(Asset)
        if organization_id:
            query = query.filter(Asset.tenant_id == organization_id)

        assets = query.all()

        # Analyze each asset
        analyses = []
        for asset in assets:
            try:
                analysis = self.analyze_asset(asset.id)
                analyses.append(analysis)
            except Exception as e:
                print(f"Error analyzing asset {asset.id}: {str(e)}")
                continue

        # Sort by risk score (highest risk first)
        analyses.sort(key=lambda x: x['prediction']['risk_score'], reverse=True)

        return analyses

    def get_high_risk_assets(self, organization_id: Optional[int] = None,
                            risk_threshold: float = 0.6) -> List[Dict]:
        """
        Get assets that require immediate attention

        Args:
            organization_id: Filter by organization
            risk_threshold: Minimum risk score to include (default 0.6 = HIGH)

        Returns:
            List of high-risk asset analyses
        """
        all_analyses = self.analyze_all_assets(organization_id)

        high_risk = [
            analysis for analysis in all_analyses
            if analysis['prediction']['risk_score'] >= risk_threshold
        ]

        return high_risk

    def get_maintenance_schedule_recommendations(self,
                                                 organization_id: Optional[int] = None,
                                                 days_ahead: int = 30) -> List[Dict]:
        """
        Generate maintenance schedule for upcoming period

        Args:
            organization_id: Filter by organization
            days_ahead: Number of days to schedule ahead

        Returns:
            List of recommended maintenance actions with timing
        """
        all_analyses = self.analyze_all_assets(organization_id)

        cutoff_date = datetime.now() + timedelta(days=days_ahead)

        schedule = []
        for analysis in all_analyses:
            predicted_date = analysis['prediction']['predicted_failure_date']

            if predicted_date and predicted_date <= cutoff_date:
                schedule.append({
                    'asset_id': analysis['asset_info']['id'],
                    'asset_name': analysis['asset_info']['name'],
                    'asset_tag': analysis['asset_info']['asset_tag'],
                    'location': analysis['asset_info']['location'],
                    'scheduled_date': predicted_date,
                    'risk_score': analysis['prediction']['risk_score'],
                    'priority': self._determine_priority(analysis['prediction']['risk_score']),
                    'action': analysis['prediction']['recommended_action'],
                    'reasoning': analysis['prediction']['reasoning'],
                    'days_until': (predicted_date - datetime.now()).days
                })

        # Sort by date (soonest first)
        schedule.sort(key=lambda x: x['scheduled_date'])

        return schedule

    def get_health_dashboard_summary(self, organization_id: Optional[int] = None) -> Dict:
        """
        Generate high-level health dashboard statistics

        Args:
            organization_id: Filter by organization

        Returns:
            Dashboard summary with key metrics
        """
        all_analyses = self.analyze_all_assets(organization_id)

        if not all_analyses:
            return {
                'total_assets': 0,
                'average_health': 0,
                'critical_assets': 0,
                'high_risk_assets': 0,
                'medium_risk_assets': 0,
                'low_risk_assets': 0,
                'upcoming_maintenance': 0
            }

        # Calculate risk distribution
        critical = sum(1 for a in all_analyses if a['prediction']['risk_score'] >= 0.8)
        high_risk = sum(1 for a in all_analyses if 0.6 <= a['prediction']['risk_score'] < 0.8)
        medium_risk = sum(1 for a in all_analyses if 0.4 <= a['prediction']['risk_score'] < 0.6)
        low_risk = sum(1 for a in all_analyses if a['prediction']['risk_score'] < 0.4)

        # Calculate average health
        avg_health = sum(a['health_score'] for a in all_analyses) / len(all_analyses)

        # Count upcoming maintenance (next 30 days)
        thirty_days = datetime.now() + timedelta(days=30)
        upcoming = sum(
            1 for a in all_analyses
            if a['prediction']['predicted_failure_date']
            and a['prediction']['predicted_failure_date'] <= thirty_days
        )

        return {
            'total_assets': len(all_analyses),
            'average_health': round(avg_health, 1),
            'critical_assets': critical,
            'high_risk_assets': high_risk,
            'medium_risk_assets': medium_risk,
            'low_risk_assets': low_risk,
            'upcoming_maintenance': upcoming,
            'risk_distribution': {
                'critical': critical,
                'high': high_risk,
                'medium': medium_risk,
                'low': low_risk
            },
            'health_distribution': self._calculate_health_distribution(all_analyses)
        }

    def _calculate_maintenance_summary(self, history: List[MaintenanceRequest]) -> Dict:
        """
        Calculate statistics from maintenance history

        Args:
            history: List of maintenance requests

        Returns:
            Summary statistics
        """
        if not history:
            return {
                'total_requests': 0,
                'recent_requests_30d': 0,
                'recent_requests_90d': 0,
                'average_resolution_days': 0,
                'last_maintenance_date': None
            }

        now = datetime.now()
        thirty_days_ago = now - timedelta(days=30)
        ninety_days_ago = now - timedelta(days=90)

        recent_30d = sum(1 for r in history if r.created_at >= thirty_days_ago)
        recent_90d = sum(1 for r in history if r.created_at >= ninety_days_ago)

        # Calculate average resolution time for completed requests
        completed = [r for r in history if r.status == 'completed' and r.updated_at]
        if completed:
            avg_resolution = sum(
                (r.updated_at - r.created_at).days for r in completed
            ) / len(completed)
        else:
            avg_resolution = 0

        return {
            'total_requests': len(history),
            'recent_requests_30d': recent_30d,
            'recent_requests_90d': recent_90d,
            'average_resolution_days': round(avg_resolution, 1),
            'last_maintenance_date': history[0].created_at if history else None
        }

    def _generate_recommendations(self, asset: Asset, health_score: float,
                                 prediction: Dict, maintenance_summary: Dict) -> List[str]:
        """
        Generate actionable recommendations based on analysis

        Args:
            asset: Asset being analyzed
            health_score: Calculated health score
            prediction: Prediction results
            maintenance_summary: Historical maintenance data

        Returns:
            List of recommendation strings
        """
        recommendations = []

        risk_score = prediction['risk_score']

        # Risk-based recommendations
        if risk_score >= 0.8:
            recommendations.append("🚨 URGENT: Immediate maintenance required to prevent failure")
            recommendations.append("Consider taking asset offline until maintenance is completed")
        elif risk_score >= 0.6:
            recommendations.append("⚠️ Schedule preventive maintenance within 7 days")
            recommendations.append("Increase monitoring frequency")
        elif risk_score >= 0.4:
            recommendations.append("📋 Plan preventive maintenance within 30 days")

        # Health-based recommendations
        if health_score < 40:
            recommendations.append("Poor asset health detected - consider replacement evaluation")
        elif health_score < 60:
            recommendations.append("Asset health declining - schedule inspection")

        # Maintenance frequency recommendations
        if maintenance_summary['recent_requests_30d'] >= 3:
            recommendations.append("High maintenance frequency - investigate root cause")
            recommendations.append("Consider asset replacement vs continued repairs")
        elif maintenance_summary['recent_requests_90d'] == 0 and risk_score < 0.3:
            recommendations.append("✅ Asset performing well - continue routine monitoring")

        # Age-based recommendations
        if asset.purchase_date:
            age_years = (datetime.now().date() - asset.purchase_date).days / 365
            if age_years > 10:
                recommendations.append("Asset exceeds typical service life - plan replacement")
            elif age_years > 7:
                recommendations.append("Asset approaching end of service life - budget for replacement")

        # Condition-based recommendations
        condition_value = asset.condition.value if hasattr(asset.condition, 'value') else str(asset.condition)
        if condition_value.lower() in ['poor', 'critical']:
            recommendations.append(f"Asset condition is {condition_value} - prioritize attention")

        # Default recommendation
        if not recommendations:
            recommendations.append("✅ Continue routine maintenance schedule")
            recommendations.append("Asset is operating within normal parameters")

        return recommendations

    def _determine_priority(self, risk_score: float) -> str:
        """
        Determine priority level from risk score

        Args:
            risk_score: Risk score (0-1)

        Returns:
            Priority level string
        """
        if risk_score >= 0.8:
            return "CRITICAL"
        elif risk_score >= 0.6:
            return "HIGH"
        elif risk_score >= 0.4:
            return "MEDIUM"
        else:
            return "LOW"

    def _calculate_health_distribution(self, analyses: List[Dict]) -> Dict:
        """
        Calculate distribution of health scores

        Args:
            analyses: List of asset analyses

        Returns:
            Health distribution by category
        """
        excellent = sum(1 for a in analyses if a['health_score'] >= 80)
        good = sum(1 for a in analyses if 60 <= a['health_score'] < 80)
        fair = sum(1 for a in analyses if 40 <= a['health_score'] < 60)
        poor = sum(1 for a in analyses if 20 <= a['health_score'] < 40)
        critical = sum(1 for a in analyses if a['health_score'] < 20)

        return {
            'excellent': excellent,
            'good': good,
            'fair': fair,
            'poor': poor,
            'critical': critical
        }
