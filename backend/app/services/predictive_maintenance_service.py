"""
Predictive Maintenance Service - Main Orchestration Layer

This is the main facade for the predictive maintenance engine.
It orchestrates all components to provide comprehensive intelligent maintenance management.

Components orchestrated:
- Prediction Strategy (failure prediction algorithms)
- Asset Health Service (health analysis)
- Smart Assignment Service (intelligent technician assignment)

Author: Sifiso Shezi (ARISAN SIFISO)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.services.prediction_strategy import RuleBasedStrategy, PredictionStrategy
from app.services.asset_health_service import AssetHealthService
from app.services.smart_assignment_service import SmartAssignmentService
from app.models.asset import Asset
from app.models.request import MaintenanceRequest, RequestStatus, RequestPriority


class PredictiveMaintenanceService:
    """
    Main service orchestrating all predictive maintenance features

    This is the single entry point for controllers to access:
    - Asset health monitoring
    - Failure predictions
    - Smart technician assignment
    - Maintenance scheduling recommendations
    - Dashboard analytics
    """

    def __init__(self, db: Session, strategy: Optional[PredictionStrategy] = None):
        """
        Initialize with database session and optional prediction strategy

        Args:
            db: SQLAlchemy database session
            strategy: Prediction strategy (defaults to RuleBasedStrategy)
        """
        self.db = db
        self.strategy = strategy or RuleBasedStrategy()

        # Initialize sub-services
        self.health_service = AssetHealthService(db, self.strategy)
        self.assignment_service = SmartAssignmentService(db)

    def set_strategy(self, strategy: PredictionStrategy):
        """
        Change prediction strategy at runtime

        Args:
            strategy: New prediction strategy to use
        """
        self.strategy = strategy
        self.health_service.set_strategy(strategy)

    # ========== Asset Health & Predictions ==========

    def get_asset_health(self, asset_id: int) -> Dict:
        """
        Get comprehensive health analysis for an asset

        Args:
            asset_id: Asset ID to analyze

        Returns:
            Complete health analysis with predictions and recommendations
        """
        return self.health_service.analyze_asset(asset_id)

    def get_all_asset_health(self, organization_id: Optional[int] = None) -> List[Dict]:
        """
        Get health analysis for all assets

        Args:
            organization_id: Filter by organization (for multi-tenant)

        Returns:
            List of asset health analyses
        """
        return self.health_service.analyze_all_assets(organization_id)

    def get_critical_assets(self, organization_id: Optional[int] = None) -> List[Dict]:
        """
        Get assets requiring immediate attention

        Args:
            organization_id: Filter by organization

        Returns:
            List of high-risk assets
        """
        return self.health_service.get_high_risk_assets(organization_id, risk_threshold=0.6)

    def get_dashboard_summary(self, organization_id: Optional[int] = None) -> Dict:
        """
        Get high-level predictive maintenance dashboard data

        Args:
            organization_id: Filter by organization

        Returns:
            Dashboard summary statistics
        """
        health_summary = self.health_service.get_health_dashboard_summary(organization_id)
        workload_summary = self._get_workload_summary(organization_id)
        upcoming_maintenance = self.get_maintenance_schedule(organization_id, days_ahead=30)

        return {
            'health_overview': health_summary,
            'workload_overview': workload_summary,
            'upcoming_maintenance_count': len(upcoming_maintenance),
            'next_7_days': [m for m in upcoming_maintenance if m['days_until'] <= 7],
            'generated_at': datetime.now()
        }

    # ========== Maintenance Scheduling ==========

    def get_maintenance_schedule(self, organization_id: Optional[int] = None,
                                 days_ahead: int = 30) -> List[Dict]:
        """
        Get recommended maintenance schedule based on predictions

        Args:
            organization_id: Filter by organization
            days_ahead: Number of days to schedule ahead

        Returns:
            List of scheduled maintenance recommendations
        """
        return self.health_service.get_maintenance_schedule_recommendations(
            organization_id, days_ahead
        )

    def create_preventive_maintenance_request(self, asset_id: int, auto_assign: bool = True) -> Dict:
        """
        Create a preventive maintenance request based on predictions

        Args:
            asset_id: Asset requiring maintenance
            auto_assign: Whether to automatically assign a technician

        Returns:
            Created request details
        """
        # Get asset health analysis
        health_data = self.health_service.analyze_asset(asset_id)

        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        # Create the maintenance request
        request = MaintenanceRequest(
            title=f"Preventive Maintenance - {asset.name}",
            description=f"Predicted maintenance based on health analysis.\n\n{health_data['prediction']['reasoning']}\n\nRisk Score: {health_data['prediction']['risk_score']}\nHealth Score: {health_data['health_score']}/100",
            asset_id=asset_id,
            submitter_id=None,  # System-generated
            priority=self._determine_priority_from_risk(health_data['prediction']['risk_score']),
            status=RequestStatus.SUBMITTED,
            request_type='preventive',
            tenant_id=asset.tenant_id,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )

        self.db.add(request)
        self.db.commit()
        self.db.refresh(request)

        # Auto-assign if requested
        assignment_result = None
        if auto_assign:
            try:
                assignment_result = self.assignment_service.assign_best_technician(request.id)
            except Exception as e:
                print(f"Auto-assignment failed: {str(e)}")

        return {
            'request_id': request.id,
            'request_title': request.title,
            'asset_id': asset_id,
            'asset_name': asset.name,
            'priority': request.priority,
            'status': request.status,
            'prediction_data': health_data['prediction'],
            'assignment': assignment_result,
            'created_at': request.created_at
        }

    # ========== Smart Assignment ==========

    def auto_assign_request(self, request_id: int) -> Optional[Dict]:
        """
        Automatically assign a maintenance request to the best technician

        Args:
            request_id: Maintenance request ID

        Returns:
            Assignment details or None if no suitable technician
        """
        return self.assignment_service.assign_best_technician(request_id)

    def get_technician_workload(self, organization_id: Optional[int] = None) -> List[Dict]:
        """
        Get current workload distribution across technicians

        Args:
            organization_id: Filter by organization

        Returns:
            List of technician workload data
        """
        return self.assignment_service.get_workload_distribution(organization_id)

    def get_reassignment_recommendations(self, organization_id: Optional[int] = None) -> List[Dict]:
        """
        Get recommendations for load balancing through reassignment

        Args:
            organization_id: Filter by organization

        Returns:
            List of recommended reassignments
        """
        return self.assignment_service.recommend_reassignments(organization_id)

    # ========== Insights & Analytics ==========

    def get_predictive_insights(self, organization_id: Optional[int] = None) -> Dict:
        """
        Get comprehensive predictive insights for the dashboard

        Args:
            organization_id: Filter by organization

        Returns:
            Complete insights package with trends, recommendations, and alerts
        """
        # Get all asset health data
        all_assets = self.health_service.analyze_all_assets(organization_id)

        # Get maintenance schedule
        schedule = self.get_maintenance_schedule(organization_id, days_ahead=90)

        # Get workload data
        workload = self.get_technician_workload(organization_id)

        # Calculate trends
        trends = self._calculate_trends(all_assets, schedule)

        # Generate actionable recommendations
        recommendations = self._generate_recommendations(all_assets, schedule, workload)

        # Identify urgent alerts
        alerts = self._generate_alerts(all_assets, schedule, workload)

        return {
            'summary': {
                'total_assets': len(all_assets),
                'critical_assets': len([a for a in all_assets if a['prediction']['risk_score'] >= 0.8]),
                'upcoming_maintenance_30d': len([s for s in schedule if s['days_until'] <= 30]),
                'upcoming_maintenance_7d': len([s for s in schedule if s['days_until'] <= 7]),
                'average_health': sum(a['health_score'] for a in all_assets) / len(all_assets) if all_assets else 0,
                'average_risk': sum(a['prediction']['risk_score'] for a in all_assets) / len(all_assets) if all_assets else 0
            },
            'trends': trends,
            'recommendations': recommendations,
            'alerts': alerts,
            'top_risk_assets': sorted(all_assets, key=lambda x: x['prediction']['risk_score'], reverse=True)[:5],
            'maintenance_calendar': self._create_maintenance_calendar(schedule),
            'workload_status': self._summarize_workload(workload),
            'generated_at': datetime.now()
        }

    def get_asset_history_insights(self, asset_id: int) -> Dict:
        """
        Get historical trends and insights for a specific asset

        Args:
            asset_id: Asset ID to analyze

        Returns:
            Historical trends and pattern analysis
        """
        asset = self.db.query(Asset).filter(Asset.id == asset_id).first()
        if not asset:
            raise ValueError(f"Asset {asset_id} not found")

        # Get maintenance history
        history = self.db.query(MaintenanceRequest).filter(
            MaintenanceRequest.asset_id == asset_id
        ).order_by(MaintenanceRequest.created_at).all()

        # Current health analysis
        current_health = self.health_service.analyze_asset(asset_id)

        # Calculate trends
        if len(history) >= 3:
            # Analyze maintenance frequency over time
            frequency_trend = self._analyze_frequency_trend(history)

            # Calculate MTBF trend
            mtbf_trend = self._analyze_mtbf_trend(history)
        else:
            frequency_trend = "Insufficient data for trend analysis"
            mtbf_trend = "Insufficient data for trend analysis"

        return {
            'asset_id': asset_id,
            'asset_name': asset.name,
            'current_health': current_health,
            'maintenance_history_count': len(history),
            'first_maintenance': history[0].created_at if history else None,
            'last_maintenance': history[-1].created_at if history else None,
            'frequency_trend': frequency_trend,
            'mtbf_trend': mtbf_trend,
            'total_downtime_days': self._calculate_total_downtime(history),
            'cost_analysis': self._estimate_maintenance_costs(asset, history)
        }

    # ========== Private Helper Methods ==========

    def _get_workload_summary(self, organization_id: Optional[int] = None) -> Dict:
        """Calculate summary workload statistics"""
        workload_data = self.assignment_service.get_workload_distribution(organization_id)

        if not workload_data:
            return {
                'total_technicians': 0,
                'average_workload': 0,
                'overloaded_technicians': 0,
                'available_technicians': 0
            }

        total_active = sum(t['active_requests'] for t in workload_data)
        avg_workload = total_active / len(workload_data) if workload_data else 0

        return {
            'total_technicians': len(workload_data),
            'total_active_requests': total_active,
            'average_workload': round(avg_workload, 1),
            'overloaded_technicians': len([t for t in workload_data if t['active_requests'] > 6]),
            'available_technicians': len([t for t in workload_data if t['active_requests'] == 0]),
            'balanced': max(t['active_requests'] for t in workload_data) - min(t['active_requests'] for t in workload_data) <= 3 if workload_data else True
        }

    def _determine_priority_from_risk(self, risk_score: float) -> RequestPriority:
        """Convert risk score to request priority"""
        if risk_score >= 0.8:
            return RequestPriority.HIGH
        elif risk_score >= 0.5:
            return RequestPriority.MEDIUM
        else:
            return RequestPriority.LOW

    def _calculate_trends(self, assets: List[Dict], schedule: List[Dict]) -> Dict:
        """Calculate trend data from asset analyses"""
        if not assets:
            return {}

        # Health trend
        avg_health = sum(a['health_score'] for a in assets) / len(assets)
        critical_count = len([a for a in assets if a['prediction']['risk_score'] >= 0.8])

        # Maintenance workload trend (next 30 days)
        next_30_days = len([s for s in schedule if s['days_until'] <= 30])

        return {
            'average_health': round(avg_health, 1),
            'health_status': 'Good' if avg_health >= 70 else 'Fair' if avg_health >= 50 else 'Poor',
            'critical_assets': critical_count,
            'maintenance_workload_30d': next_30_days,
            'workload_level': 'Heavy' if next_30_days > 10 else 'Moderate' if next_30_days > 5 else 'Light'
        }

    def _generate_recommendations(self, assets: List[Dict], schedule: List[Dict],
                                 workload: List[Dict]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []

        # Critical assets
        critical = [a for a in assets if a['prediction']['risk_score'] >= 0.8]
        if critical:
            recommendations.append(f"⚠️ {len(critical)} assets require immediate attention")

        # Upcoming maintenance
        next_7_days = [s for s in schedule if s['days_until'] <= 7]
        if next_7_days:
            recommendations.append(f"📅 {len(next_7_days)} maintenance tasks due within 7 days")

        # Workload balance
        if workload:
            overloaded = [t for t in workload if t['active_requests'] > 6]
            if overloaded:
                recommendations.append(f"⚖️ Consider load balancing - {len(overloaded)} technicians overloaded")

        # Health trends
        poor_health = [a for a in assets if a['health_score'] < 40]
        if poor_health:
            recommendations.append(f"🔧 {len(poor_health)} assets in poor health - consider replacement")

        if not recommendations:
            recommendations.append("✅ All systems operating normally")

        return recommendations

    def _generate_alerts(self, assets: List[Dict], schedule: List[Dict],
                        workload: List[Dict]) -> List[Dict]:
        """Generate urgent alerts"""
        alerts = []

        # Critical assets
        for asset in assets:
            if asset['prediction']['risk_score'] >= 0.9:
                alerts.append({
                    'type': 'critical',
                    'title': 'Critical Asset Failure Risk',
                    'message': f"{asset['asset_info']['name']} has a {asset['prediction']['risk_score']*100:.0f}% failure risk",
                    'asset_id': asset['asset_info']['id'],
                    'severity': 'critical',
                    'action_required': 'immediate'
                })

        # Overdue maintenance
        overdue = [s for s in schedule if s['days_until'] < 0]
        for item in overdue:
            alerts.append({
                'type': 'overdue',
                'title': 'Overdue Maintenance',
                'message': f"{item['asset_name']} maintenance is {abs(item['days_until'])} days overdue",
                'asset_id': item['asset_id'],
                'severity': 'high',
                'action_required': 'urgent'
            })

        return alerts

    def _create_maintenance_calendar(self, schedule: List[Dict]) -> Dict:
        """Create a 30-day maintenance calendar"""
        calendar = {}

        for item in schedule:
            if item['days_until'] <= 30:
                date_str = item['scheduled_date'].strftime('%Y-%m-%d')
                if date_str not in calendar:
                    calendar[date_str] = []

                calendar[date_str].append({
                    'asset_name': item['asset_name'],
                    'priority': item['priority'],
                    'action': item['action']
                })

        return calendar

    def _summarize_workload(self, workload: List[Dict]) -> Dict:
        """Summarize workload status"""
        if not workload:
            return {'status': 'No technicians available'}

        total_requests = sum(t['active_requests'] for t in workload)
        return {
            'total_active_requests': total_requests,
            'technicians': len(workload),
            'average_per_tech': round(total_requests / len(workload), 1),
            'status': 'Balanced' if all(t['active_requests'] <= 5 for t in workload) else 'Imbalanced'
        }

    def _analyze_frequency_trend(self, history: List[MaintenanceRequest]) -> str:
        """Analyze if maintenance frequency is increasing or decreasing"""
        if len(history) < 6:
            return "Insufficient data"

        # Compare first half vs second half
        mid = len(history) // 2
        first_half = history[:mid]
        second_half = history[mid:]

        first_span = (first_half[-1].created_at - first_half[0].created_at).days or 1
        second_span = (second_half[-1].created_at - second_half[0].created_at).days or 1

        first_freq = len(first_half) / (first_span / 30)  # requests per month
        second_freq = len(second_half) / (second_span / 30)

        if second_freq > first_freq * 1.3:
            return "Increasing (deteriorating)"
        elif second_freq < first_freq * 0.7:
            return "Decreasing (improving)"
        else:
            return "Stable"

    def _analyze_mtbf_trend(self, history: List[MaintenanceRequest]) -> str:
        """Analyze Mean Time Between Failures trend"""
        if len(history) < 4:
            return "Insufficient data"

        intervals = []
        for i in range(1, len(history)):
            days = (history[i].created_at - history[i-1].created_at).days
            intervals.append(days)

        if len(intervals) < 3:
            return "Insufficient data"

        # Compare early vs recent intervals
        early_avg = sum(intervals[:len(intervals)//2]) / (len(intervals)//2)
        recent_avg = sum(intervals[len(intervals)//2:]) / (len(intervals) - len(intervals)//2)

        if recent_avg < early_avg * 0.7:
            return "Decreasing (more frequent failures)"
        elif recent_avg > early_avg * 1.3:
            return "Increasing (fewer failures)"
        else:
            return "Stable"

    def _calculate_total_downtime(self, history: List[MaintenanceRequest]) -> float:
        """Calculate total downtime in days"""
        total_days = 0
        for request in history:
            if request.updated_at and request.status == RequestStatus.COMPLETED:
                days = (request.updated_at - request.created_at).days
                total_days += days
        return round(total_days, 1)

    def _estimate_maintenance_costs(self, asset: Asset, history: List[MaintenanceRequest]) -> Dict:
        """Estimate maintenance costs (placeholder for future cost tracking)"""
        # This would integrate with actual cost tracking in the future
        return {
            'total_maintenance_events': len(history),
            'estimated_cost': 'Cost tracking not yet implemented',
            'cost_trend': 'Enable cost tracking for insights'
        }
