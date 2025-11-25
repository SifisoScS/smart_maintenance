"""
Smart Technician Assignment Service - Intelligent Work Distribution

This service implements intelligent assignment algorithms that consider:
- Technician workload and availability
- MaintenanceRequest urgency and predicted failure dates
- Technician skills and specialization
- Location proximity (future enhancement)
- Historical performance (future enhancement)

Author: Sifiso Shezi (ARISAN SIFISO)
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.user import User, UserRole
from app.models.request import MaintenanceRequest, RequestStatus, RequestPriority
from app.models.asset import Asset


class SmartAssignmentService:
    """
    Intelligent technician assignment using rule-based algorithms

    Considers multiple factors to optimize work distribution and response times.
    """

    def __init__(self, db: Session):
        """
        Initialize with database session

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def assign_best_technician(self, request_id: int) -> Optional[Dict]:
        """
        Automatically assign the best-fit technician to a maintenance request

        Args:
            request_id: ID of maintenance request to assign

        Returns:
            Dict with assignment details or None if no suitable technician found
        """
        # Fetch the request
        request = self.db.query(MaintenanceRequest).filter(
            MaintenanceRequest.id == request_id
        ).first()

        if not request:
            raise ValueError(f"Maintenance request {request_id} not found")

        if request.assigned_technician_id:
            raise ValueError(f"MaintenanceRequest {request_id} is already assigned")

        # Get all available technicians
        technicians = self.db.query(User).filter(
            User.role == UserRole.TECHNICIAN,
            User.is_active == True
        ).all()

        if not technicians:
            return None

        # Score each technician
        scored_technicians = []
        for tech in technicians:
            score = self._calculate_technician_score(tech, request)
            scored_technicians.append({
                'technician': tech,
                'score': score,
                'workload': self._get_workload(tech.id),
                'availability': self._calculate_availability(tech.id)
            })

        # Sort by score (highest first)
        scored_technicians.sort(key=lambda x: x['score'], reverse=True)

        # Assign to best-fit technician
        best_match = scored_technicians[0]
        request.assigned_technician_id = best_match['technician'].id
        request.status = RequestStatus.ASSIGNED
        request.updated_at = datetime.now()

        self.db.commit()

        return {
            'request_id': request.id,
            'assigned_technician_id': best_match['technician'].id,
            'technician_name': best_match['technician'].full_name,
            'assignment_score': round(best_match['score'], 2),
            'assignment_reason': self._generate_assignment_reasoning(
                best_match, scored_technicians
            ),
            'assigned_at': datetime.now()
        }

    def get_workload_distribution(self, organization_id: Optional[int] = None) -> List[Dict]:
        """
        Get current workload distribution across all technicians

        Args:
            organization_id: Filter by organization

        Returns:
            List of technician workload data
        """
        # Build query for technicians
        tech_query = self.db.query(User).filter(
            User.role == UserRole.TECHNICIAN,
            User.is_active == True
        )

        if organization_id:
            tech_query = tech_query.filter(User.tenant_id == organization_id)

        technicians = tech_query.all()

        workload_data = []
        for tech in technicians:
            workload = self._get_detailed_workload(tech.id)
            availability = self._calculate_availability(tech.id)

            workload_data.append({
                'technician_id': tech.id,
                'technician_name': tech.full_name,
                'email': tech.email,
                'active_requests': workload['active_count'],
                'pending_requests': workload['pending_count'],
                'in_progress_requests': workload['in_progress_count'],
                'completed_last_30d': workload['completed_30d'],
                'availability_score': round(availability, 2),
                'workload_level': self._determine_workload_level(workload['active_count']),
                'avg_completion_time': workload['avg_completion_days']
            })

        # Sort by active requests (lowest first)
        workload_data.sort(key=lambda x: x['active_requests'])

        return workload_data

    def recommend_reassignments(self, organization_id: Optional[int] = None) -> List[Dict]:
        """
        Identify requests that should be reassigned for better load balancing

        Args:
            organization_id: Filter by organization

        Returns:
            List of recommended reassignments
        """
        workload_data = self.get_workload_distribution(organization_id)

        if len(workload_data) < 2:
            return []  # Need at least 2 technicians for reassignment

        # Find overloaded and underloaded technicians
        avg_workload = sum(t['active_requests'] for t in workload_data) / len(workload_data)

        overloaded = [t for t in workload_data if t['active_requests'] > avg_workload * 1.5]
        underloaded = [t for t in workload_data if t['active_requests'] < avg_workload * 0.75]

        if not overloaded or not underloaded:
            return []

        recommendations = []

        # For each overloaded technician, suggest reassignments
        for overloaded_tech in overloaded:
            # Get their active requests (lowest priority first)
            requests = self.db.query(MaintenanceRequest).filter(
                MaintenanceRequest.assigned_technician_id == overloaded_tech['technician_id'],
                MaintenanceRequest.status.in_([RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS])
            ).order_by(
                MaintenanceRequest.priority.desc()  # Low priority first
            ).all()

            for request in requests[:2]:  # Limit to 2 recommendations per tech
                # Find best underloaded technician
                best_target = min(underloaded, key=lambda x: x['active_requests'])

                recommendations.append({
                    'request_id': request.id,
                    'request_title': request.title,
                    'current_technician_id': overloaded_tech['technician_id'],
                    'current_technician_name': overloaded_tech['technician_name'],
                    'current_workload': overloaded_tech['active_requests'],
                    'recommended_technician_id': best_target['technician_id'],
                    'recommended_technician_name': best_target['technician_name'],
                    'target_workload': best_target['active_requests'],
                    'reason': f"Balance workload - {overloaded_tech['technician_name']} has {overloaded_tech['active_requests']} active requests",
                    'priority': request.priority
                })

                # Update underloaded count for next iteration
                best_target['active_requests'] += 1

        return recommendations

    def _calculate_technician_score(self, technician: User, request: MaintenanceRequest) -> float:
        """
        Calculate fitness score for technician-request pairing

        Args:
            technician: Technician user
            request: Maintenance request

        Returns:
            Score (0-100, higher is better)
        """
        score = 50.0  # Base score

        # Factor 1: Current workload (30% weight)
        workload = self._get_workload(technician.id)
        if workload == 0:
            workload_score = 30
        elif workload <= 2:
            workload_score = 25
        elif workload <= 4:
            workload_score = 20
        elif workload <= 6:
            workload_score = 15
        else:
            workload_score = 5

        score += workload_score

        # Factor 2: MaintenanceRequest urgency alignment (25% weight)
        if request.priority == RequestPriority.HIGH or request.priority == RequestPriority.URGENT:
            # High priority - assign to less loaded techs
            if workload <= 2:
                score += 25
            elif workload <= 4:
                score += 15
            else:
                score += 5
        elif request.priority == RequestPriority.MEDIUM:
            if workload <= 4:
                score += 20
            else:
                score += 10
        else:  # low priority
            if workload <= 6:
                score += 15
            else:
                score += 10

        # Factor 3: Recent performance (15% weight)
        completion_rate = self._get_completion_rate(technician.id)
        score += completion_rate * 15

        # Factor 4: Availability (10% weight)
        availability = self._calculate_availability(technician.id)
        score += availability * 10

        return min(100.0, max(0.0, score))

    def _get_workload(self, technician_id: int) -> int:
        """
        Get current active workload for a technician

        Args:
            technician_id: Technician user ID

        Returns:
            Number of active requests
        """
        count = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.assigned_technician_id == technician_id,
            MaintenanceRequest.status.in_([RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS])
        ).scalar()

        return count or 0

    def _get_detailed_workload(self, technician_id: int) -> Dict:
        """
        Get detailed workload metrics for a technician

        Args:
            technician_id: Technician user ID

        Returns:
            Dict with workload details
        """
        # Active requests
        active_count = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.assigned_technician_id == technician_id,
            MaintenanceRequest.status.in_([RequestStatus.ASSIGNED, RequestStatus.IN_PROGRESS])
        ).scalar() or 0

        # Pending (assigned but not started)
        pending_count = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.assigned_technician_id == technician_id,
            MaintenanceRequest.status == RequestStatus.ASSIGNED
        ).scalar() or 0

        # In progress
        in_progress_count = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.assigned_technician_id == technician_id,
            MaintenanceRequest.status == RequestStatus.IN_PROGRESS
        ).scalar() or 0

        # Completed in last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        completed_30d = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.assigned_technician_id == technician_id,
            MaintenanceRequest.status == RequestStatus.COMPLETED,
            MaintenanceRequest.updated_at >= thirty_days_ago
        ).scalar() or 0

        # Average completion time
        completed_requests = self.db.query(MaintenanceRequest).filter(
            MaintenanceRequest.assigned_technician_id == technician_id,
            MaintenanceRequest.status == RequestStatus.COMPLETED,
            MaintenanceRequest.updated_at.isnot(None)
        ).limit(20).all()

        if completed_requests:
            avg_days = sum(
                (r.updated_at - r.created_at).days for r in completed_requests
            ) / len(completed_requests)
        else:
            avg_days = 0

        return {
            'active_count': active_count,
            'pending_count': pending_count,
            'in_progress_count': in_progress_count,
            'completed_30d': completed_30d,
            'avg_completion_days': round(avg_days, 1)
        }

    def _calculate_availability(self, technician_id: int) -> float:
        """
        Calculate availability score based on workload

        Args:
            technician_id: Technician user ID

        Returns:
            Availability score (0-1, higher is better)
        """
        workload = self._get_workload(technician_id)

        if workload == 0:
            return 1.0
        elif workload <= 2:
            return 0.9
        elif workload <= 4:
            return 0.7
        elif workload <= 6:
            return 0.5
        elif workload <= 8:
            return 0.3
        else:
            return 0.1

    def _get_completion_rate(self, technician_id: int) -> float:
        """
        Calculate recent completion rate (completed / total assigned)

        Args:
            technician_id: Technician user ID

        Returns:
            Completion rate (0-1)
        """
        thirty_days_ago = datetime.now() - timedelta(days=30)

        total = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.assigned_technician_id == technician_id,
            MaintenanceRequest.created_at >= thirty_days_ago
        ).scalar() or 0

        if total == 0:
            return 0.8  # Default to good score for new technicians

        completed = self.db.query(func.count(MaintenanceRequest.id)).filter(
            MaintenanceRequest.assigned_technician_id == technician_id,
            MaintenanceRequest.status == RequestStatus.COMPLETED,
            MaintenanceRequest.created_at >= thirty_days_ago
        ).scalar() or 0

        return completed / total

    def _determine_workload_level(self, active_count: int) -> str:
        """
        Categorize workload level

        Args:
            active_count: Number of active requests

        Returns:
            Workload level string
        """
        if active_count == 0:
            return "Available"
        elif active_count <= 2:
            return "Light"
        elif active_count <= 4:
            return "Moderate"
        elif active_count <= 6:
            return "Heavy"
        else:
            return "Overloaded"

    def _generate_assignment_reasoning(self, best_match: Dict,
                                      all_candidates: List[Dict]) -> str:
        """
        Generate human-readable explanation for assignment choice

        Args:
            best_match: Selected technician data
            all_candidates: All candidate technicians

        Returns:
            Reasoning string
        """
        tech_name = best_match['technician'].full_name
        workload = best_match['workload']
        score = best_match['score']

        reasons = [f"Selected {tech_name} (score: {score:.1f})"]

        if workload == 0:
            reasons.append("currently available with no active requests")
        elif workload <= 2:
            reasons.append(f"light workload ({workload} active requests)")
        elif workload <= 4:
            reasons.append(f"moderate workload ({workload} active requests)")
        else:
            reasons.append(f"best available option despite {workload} active requests")

        # Compare to others
        if len(all_candidates) > 1:
            avg_score = sum(c['score'] for c in all_candidates) / len(all_candidates)
            if score > avg_score + 10:
                reasons.append("significantly better fit than alternatives")

        return " - ".join(reasons)
