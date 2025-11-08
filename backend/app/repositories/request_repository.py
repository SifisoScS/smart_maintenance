"""
Request Repository with maintenance request-specific data access methods.

Handles polymorphic MaintenanceRequest and its subtypes.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from app.repositories.base_repository import BaseRepository
from app.models.request import (
    MaintenanceRequest,
    ElectricalRequest,
    PlumbingRequest,
    HVACRequest,
    RequestStatus,
    RequestPriority,
    RequestType
)


class RequestRepository(BaseRepository[MaintenanceRequest]):
    """
    Repository for MaintenanceRequest model and its subtypes.

    OOP Principles:
    - Polymorphism: Works with base and specialized request types
    - Inheritance: Extends BaseRepository functionality
    - Abstraction: Hides query complexity behind simple methods
    """

    def __init__(self):
        """Initialize with MaintenanceRequest model class"""
        super().__init__(MaintenanceRequest)

    def get_by_status(self, status: RequestStatus) -> List[MaintenanceRequest]:
        """
        Get all requests with specific status.

        Args:
            status: RequestStatus enum value

        Returns:
            List of requests with the status (all types)
        """
        return self.get_by_filter(status=status)

    def get_by_priority(self, priority: RequestPriority) -> List[MaintenanceRequest]:
        """
        Get all requests with specific priority.

        Args:
            priority: RequestPriority enum value

        Returns:
            List of requests with the priority
        """
        return self.get_by_filter(priority=priority)

    def get_by_type(self, request_type: RequestType) -> List[MaintenanceRequest]:
        """
        Get all requests of specific type.

        Args:
            request_type: RequestType enum value

        Returns:
            List of requests of the specified type

        Note: Returns polymorphic instances (ElectricalRequest, PlumbingRequest, etc.)
        """
        return self.get_by_filter(type=request_type.value)

    def get_open_requests(self) -> List[MaintenanceRequest]:
        """
        Get all open (not completed or cancelled) requests.

        Returns:
            List of open requests
        """
        from app.database import db

        return db.session.query(MaintenanceRequest).filter(
            MaintenanceRequest.status.notin_([RequestStatus.COMPLETED, RequestStatus.CANCELLED])
        ).all()

    def get_unassigned_requests(self) -> List[MaintenanceRequest]:
        """
        Get all requests not yet assigned to a technician.

        Returns:
            List of unassigned requests
        """
        from app.database import db

        return db.session.query(MaintenanceRequest).filter(
            MaintenanceRequest.assigned_technician_id.is_(None),
            MaintenanceRequest.status != RequestStatus.CANCELLED
        ).all()

    def get_requests_by_submitter(self, submitter_id: int) -> List[MaintenanceRequest]:
        """
        Get all requests submitted by specific user.

        Args:
            submitter_id: User ID of submitter

        Returns:
            List of requests from submitter
        """
        return self.get_by_filter(submitter_id=submitter_id)

    def get_requests_by_technician(self, technician_id: int) -> List[MaintenanceRequest]:
        """
        Get all requests assigned to specific technician.

        Args:
            technician_id: User ID of technician

        Returns:
            List of assigned requests
        """
        return self.get_by_filter(assigned_technician_id=technician_id)

    def get_open_requests_by_technician(self, technician_id: int) -> List[MaintenanceRequest]:
        """
        Get open requests assigned to specific technician.

        Args:
            technician_id: User ID of technician

        Returns:
            List of open requests for technician
        """
        from app.database import db

        return db.session.query(MaintenanceRequest).filter(
            MaintenanceRequest.assigned_technician_id == technician_id,
            MaintenanceRequest.status.notin_([RequestStatus.COMPLETED, RequestStatus.CANCELLED])
        ).all()

    def get_requests_by_asset(self, asset_id: int) -> List[MaintenanceRequest]:
        """
        Get all maintenance requests for specific asset.

        Args:
            asset_id: Asset ID

        Returns:
            List of requests for the asset (maintenance history)
        """
        return self.get_by_filter(asset_id=asset_id)

    def get_urgent_requests(self) -> List[MaintenanceRequest]:
        """
        Get all urgent priority requests.

        Returns:
            List of urgent requests
        """
        return self.get_by_priority(RequestPriority.URGENT)

    def get_overdue_requests(self, days: int = 7) -> List[MaintenanceRequest]:
        """
        Get requests open longer than specified days.

        Args:
            days: Number of days threshold (default 7)

        Returns:
            List of overdue requests
        """
        from app.database import db

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        return db.session.query(MaintenanceRequest).filter(
            MaintenanceRequest.created_at < cutoff_date,
            MaintenanceRequest.status.notin_([RequestStatus.COMPLETED, RequestStatus.CANCELLED])
        ).all()

    def get_recent_requests(self, days: int = 30, limit: int = 50) -> List[MaintenanceRequest]:
        """
        Get recently created requests.

        Args:
            days: Number of days to look back (default 30)
            limit: Maximum number of requests to return (default 50)

        Returns:
            List of recent requests
        """
        from app.database import db

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        return db.session.query(MaintenanceRequest).filter(
            MaintenanceRequest.created_at >= cutoff_date
        ).order_by(
            MaintenanceRequest.created_at.desc()
        ).limit(limit).all()

    def get_completed_requests(self, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None) -> List[MaintenanceRequest]:
        """
        Get completed requests within date range.

        Args:
            start_date: Start of date range (optional)
            end_date: End of date range (optional)

        Returns:
            List of completed requests
        """
        from app.database import db

        query = db.session.query(MaintenanceRequest).filter(
            MaintenanceRequest.status == RequestStatus.COMPLETED
        )

        if start_date:
            query = query.filter(MaintenanceRequest.updated_at >= start_date)

        if end_date:
            query = query.filter(MaintenanceRequest.updated_at <= end_date)

        return query.all()

    def assign_technician(self, request_id: int, technician_id: int) -> bool:
        """
        Assign request to technician.

        Args:
            request_id: Request ID
            technician_id: Technician user ID

        Returns:
            True if successful, False if request not found

        Raises:
            ValueError: If request cannot be assigned
        """
        request = self.get_by_id(request_id)

        if request:
            request.assign_to(technician_id)
            self.update(request)
            return True

        return False

    def start_request(self, request_id: int) -> bool:
        """
        Mark request as in progress.

        Args:
            request_id: Request ID

        Returns:
            True if successful, False if request not found

        Raises:
            ValueError: If request cannot be started
        """
        request = self.get_by_id(request_id)

        if request:
            request.start_work()
            self.update(request)
            return True

        return False

    def complete_request(self, request_id: int, completion_notes: Optional[str] = None,
                        actual_hours: Optional[float] = None) -> bool:
        """
        Mark request as completed.

        Args:
            request_id: Request ID
            completion_notes: Notes about completion (optional)
            actual_hours: Actual hours worked (optional)

        Returns:
            True if successful, False if request not found

        Raises:
            ValueError: If request cannot be completed
        """
        request = self.get_by_id(request_id)

        if request:
            request.complete(completion_notes, actual_hours)
            self.update(request)
            return True

        return False

    def cancel_request(self, request_id: int, reason: Optional[str] = None) -> bool:
        """
        Cancel request.

        Args:
            request_id: Request ID
            reason: Cancellation reason (optional)

        Returns:
            True if successful, False if request not found

        Raises:
            ValueError: If request cannot be cancelled
        """
        request = self.get_by_id(request_id)

        if request:
            request.cancel(reason)
            self.update(request)
            return True

        return False

    def get_request_statistics(self) -> dict:
        """
        Get request statistics summary.

        Returns:
            Dictionary with request counts and metrics
        """
        return {
            'total': self.count(),
            'by_status': {
                'submitted': self.count(status=RequestStatus.SUBMITTED),
                'assigned': self.count(status=RequestStatus.ASSIGNED),
                'in_progress': self.count(status=RequestStatus.IN_PROGRESS),
                'on_hold': self.count(status=RequestStatus.ON_HOLD),
                'completed': self.count(status=RequestStatus.COMPLETED),
                'cancelled': self.count(status=RequestStatus.CANCELLED),
            },
            'by_priority': {
                'low': self.count(priority=RequestPriority.LOW),
                'medium': self.count(priority=RequestPriority.MEDIUM),
                'high': self.count(priority=RequestPriority.HIGH),
                'urgent': self.count(priority=RequestPriority.URGENT),
            },
            'by_type': {
                'electrical': self.count(type=RequestType.ELECTRICAL.value),
                'plumbing': self.count(type=RequestType.PLUMBING.value),
                'hvac': self.count(type=RequestType.HVAC.value),
            },
            'open_requests': len(self.get_open_requests()),
            'unassigned_requests': len(self.get_unassigned_requests()),
        }

    def get_technician_workload(self, technician_id: int) -> dict:
        """
        Get workload metrics for specific technician.

        Args:
            technician_id: Technician user ID

        Returns:
            Dictionary with workload metrics
        """
        all_requests = self.get_requests_by_technician(technician_id)
        open_requests = self.get_open_requests_by_technician(technician_id)

        return {
            'technician_id': technician_id,
            'total_assigned': len(all_requests),
            'open_requests': len(open_requests),
            'completed_requests': len([r for r in all_requests if r.is_completed]),
            'in_progress': len([r for r in open_requests if r.status == RequestStatus.IN_PROGRESS]),
            'on_hold': len([r for r in open_requests if r.status == RequestStatus.ON_HOLD]),
        }
