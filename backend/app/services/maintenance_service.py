"""
Maintenance Service - Core Business Logic

Demonstrates:
- Service Layer orchestrating multiple repositories
- Complex business rules and validation
- Pattern integration (Factory, Strategy, Repository)
- Transaction management across multiple entities
"""

from typing import Optional, Dict, List
from flask import g, has_request_context
from app.services.base_service import BaseService
from app.repositories import RequestRepository, UserRepository, AssetRepository
from app.services.notification_service import NotificationService
from app.patterns.factory import MaintenanceRequestFactory
from app.models import UserRole, RequestStatus, RequestPriority, AssetStatus
from app.database import db
from app.patterns.event_bus import EventBus
from app.events.event_types import EventTypes


class MaintenanceService(BaseService):
    """
    Service for maintenance request management.

    This is the most complex service, demonstrating:
    - Multi-repository orchestration
    - Business rule enforcement
    - Automated notifications (Observer-like behavior)
    - Factory pattern usage
    - Transaction management
    - Plan limit enforcement (multi-tenancy)

    OOP Principles:
    - Single Responsibility: Manages only maintenance request business logic
    - Dependency Injection: All dependencies injected
    - Service Layer: Orchestrates repositories and other services
    """

    def __init__(self, request_repository: RequestRepository,
                 user_repository: UserRepository,
                 asset_repository: AssetRepository,
                 notification_service: NotificationService,
                 factory: MaintenanceRequestFactory):
        """
        Initialize maintenance service with all dependencies.

        Args:
            request_repository: For request data access
            user_repository: For user lookups
            asset_repository: For asset lookups
            notification_service: For sending notifications
            factory: For creating specialized requests
        """
        super().__init__()
        self.request_repo = request_repository
        self.user_repo = user_repository
        self.asset_repo = asset_repository
        self.notification_service = notification_service
        self.factory = factory
        self.event_bus = EventBus()

    def create_request(self, request_type: str, submitter_id: int, asset_id: Optional[int] = None,
                      title: str = None, description: str = None, priority: str = 'medium',
                      **type_specific_fields) -> dict:
        """
        Create a new maintenance request.

        Business Logic:
        - Checks plan limits (multi-tenancy)
        - Validates submitter exists and is active
        - Validates asset exists
        - Creates specialized request via Factory
        - Saves to database
        - Notifies admins of new request

        Args:
            request_type: Type of request (electrical, plumbing, hvac)
            submitter_id: User ID of requester
            asset_id: Asset ID
            title: Request title
            description: Description
            priority: Priority level (default: medium)
            **type_specific_fields: Request type specific fields

        Returns:
            dict: Success/error response with request data
        """
        try:
            # Check plan limits (multi-tenancy)
            if has_request_context() and hasattr(g, 'current_tenant_id') and g.current_tenant_id:
                from app.services.tenant_service import TenantService
                tenant_service = TenantService()
                limit_check = tenant_service.check_plan_limits(g.current_tenant_id, 'requests', count=1)

                if not limit_check['allowed']:
                    return self._build_error_response(
                        limit_check['message'],
                        status_code=403
                    )

            # Validate inputs
            self._validate_required(request_type, 'request_type')
            self._validate_positive(submitter_id, 'submitter_id')
            self._validate_required(title, 'title')
            self._validate_required(description, 'description')

            # Only validate asset_id if provided
            if asset_id is not None:
                self._validate_positive(asset_id, 'asset_id')

            # Business Rule: Validate submitter exists and is active
            submitter = self.user_repo.get_by_id(submitter_id)
            if not submitter:
                return self._build_error_response("Submitter not found")
            if not submitter.is_active:
                return self._build_error_response("Submitter account is not active")

            # Business Rule: Validate asset exists (if provided)
            asset = None
            if asset_id is not None:
                asset = self.asset_repo.get_by_id(asset_id)
                if not asset:
                    return self._build_error_response("Asset not found")

            # Convert priority string to enum
            try:
                from app.models import RequestPriority, RequestType
                priority_enum = RequestPriority(priority.lower())
                request_type_enum = RequestType(request_type.lower())
            except ValueError as e:
                return self._build_error_response(f"Invalid value: {str(e)}")

            # Create request using Factory Pattern
            request = self.factory.create_request(
                request_type=request_type_enum,
                title=title,
                description=description,
                submitter_id=submitter_id,
                asset_id=asset_id,
                priority=priority_enum,
                **type_specific_fields
            )

            # Save to database
            db.session.add(request)
            db.session.commit()
            db.session.refresh(request)

            self._log_action(
                f"Request created: {request.id}",
                {'type': request_type, 'priority': priority, 'submitter': submitter.email}
            )

            # Publish REQUEST_CREATED event
            self.event_bus.publish(
                EventTypes.REQUEST_CREATED,
                {
                    'request_id': request.id,
                    'type': request.type.value if hasattr(request.type, 'value') else request.type,
                    'priority': request.priority.value if hasattr(request.priority, 'value') else request.priority,
                    'submitter_id': submitter_id,
                    'asset_id': asset_id,
                    'title': title
                },
                source='MaintenanceService.create_request'
            )

            # Business Rule: Notify admins of new request (asset may be None)
            self._notify_admins_new_request(request, submitter, asset)

            return self._build_success_response(
                data=request.to_dict(),
                message=f"Maintenance request #{request.id} created successfully"
            )

        except ValueError as e:
            db.session.rollback()
            return self._build_error_response(str(e))
        except Exception as e:
            db.session.rollback()
            return self._handle_exception(e, "create_request")

    def assign_request(self, request_id: int, technician_id: int, assigned_by_user_id: int) -> dict:
        """
        Assign maintenance request to a technician.

        Business Rules:
        - Only admins can assign requests
        - Technician must exist, be active, and have technician role
        - Request must be in assignable state (submitted/assigned)
        - Asset status updated to IN_REPAIR
        - Technician notified of assignment

        Args:
            request_id: Request ID
            technician_id: Technician user ID
            assigned_by_user_id: User ID performing assignment (must be admin)

        Returns:
            dict: Success/error response
        """
        try:
            # Validate inputs
            self._validate_positive(request_id, 'request_id')
            self._validate_positive(technician_id, 'technician_id')
            self._validate_positive(assigned_by_user_id, 'assigned_by_user_id')

            # Business Rule: Only admins can assign
            admin = self.user_repo.get_by_id(assigned_by_user_id)
            if not admin or not admin.is_admin:
                return self._build_error_response("Only administrators can assign requests")

            # Get request
            request = self.request_repo.get_by_id(request_id)
            if not request:
                return self._build_error_response("Request not found")

            # Business Rule: Request must be in assignable state
            if request.status not in [RequestStatus.SUBMITTED, RequestStatus.ASSIGNED]:
                return self._build_error_response(
                    f"Cannot assign request in {request.status.value} status"
                )

            # Business Rule: Validate technician
            technician = self.user_repo.get_by_id(technician_id)
            if not technician:
                return self._build_error_response("Technician not found")
            if not technician.is_technician:
                return self._build_error_response("User is not a technician")
            if not technician.is_active:
                return self._build_error_response("Technician account is not active")

            # Assign request
            request.assign_to(technician_id)
            updated_request = self.request_repo.update(request)

            # Business Rule: Update asset status to IN_REPAIR
            asset = self.asset_repo.get_by_id(request.asset_id)
            if asset and asset.status == AssetStatus.ACTIVE:
                self.asset_repo.mark_asset_under_repair(asset.id)

            self._log_action(
                f"Request {request_id} assigned to technician {technician_id}",
                {'assigned_by': admin.email, 'technician': technician.email}
            )

            # Publish REQUEST_ASSIGNED event
            self.event_bus.publish(
                EventTypes.REQUEST_ASSIGNED,
                {
                    'request_id': request_id,
                    'technician_id': technician_id,
                    'assigned_by': assigned_by_user_id,
                    'asset_id': request.asset_id,
                    'priority': request.priority.value
                },
                source='MaintenanceService.assign_request'
            )

            # Business Rule: Notify technician of assignment
            self.notification_service.notify_user(
                user_id=technician_id,
                subject=f"New Assignment: {request.title}",
                message=f"You have been assigned to maintenance request #{request.id}. "
                       f"Priority: {request.priority.value.upper()}. Asset: {asset.name if asset else 'N/A'}"
            )

            return self._build_success_response(
                data=updated_request.to_dict(),
                message=f"Request assigned to {technician.full_name}"
            )

        except ValueError as e:
            return self._build_error_response(str(e))
        except Exception as e:
            return self._handle_exception(e, "assign_request")

    def start_work(self, request_id: int, technician_id: int) -> dict:
        """
        Mark request as in progress.

        Business Rules:
        - Only assigned technician can start work
        - Request must be assigned
        - Submitter notified when work starts
        """
        try:
            request = self.request_repo.get_by_id(request_id)
            if not request:
                return self._build_error_response("Request not found")

            # Business Rule: Only assigned technician can start
            if request.assigned_technician_id != technician_id:
                return self._build_error_response("Only the assigned technician can start work")

            # Start work
            request.start_work()
            updated_request = self.request_repo.update(request)

            self._log_action(f"Work started on request {request_id}", {'technician_id': technician_id})

            # Publish REQUEST_STARTED event
            self.event_bus.publish(
                EventTypes.REQUEST_STARTED,
                {
                    'request_id': request_id,
                    'technician_id': technician_id,
                    'asset_id': request.asset_id
                },
                source='MaintenanceService.start_work'
            )

            # Notify submitter
            self.notification_service.notify_user(
                user_id=request.submitter_id,
                subject=f"Work Started: {request.title}",
                message=f"Work has begun on your maintenance request #{request.id}."
            )

            return self._build_success_response(
                data=updated_request.to_dict(),
                message="Work started on request"
            )

        except ValueError as e:
            return self._build_error_response(str(e))
        except Exception as e:
            return self._handle_exception(e, "start_work")

    def complete_request(self, request_id: int, technician_id: int,
                        completion_notes: str, actual_hours: Optional[float] = None) -> dict:
        """
        Complete maintenance request.

        Business Rules:
        - Only assigned technician can complete
        - Completion notes required
        - Asset status updated to ACTIVE (if it was IN_REPAIR)
        - Submitter and admins notified
        """
        try:
            request = self.request_repo.get_by_id(request_id)
            if not request:
                return self._build_error_response("Request not found")

            # Business Rule: Only assigned technician
            if request.assigned_technician_id != technician_id:
                return self._build_error_response("Only the assigned technician can complete this request")

            # Business Rule: Completion notes required
            if not completion_notes or not completion_notes.strip():
                return self._build_error_response("Completion notes are required")

            # Complete request
            request.complete(completion_notes, actual_hours)
            updated_request = self.request_repo.update(request)

            # Business Rule: Mark asset as repaired
            asset = self.asset_repo.get_by_id(request.asset_id)
            if asset and asset.status == AssetStatus.IN_REPAIR:
                self.asset_repo.mark_asset_repaired(asset.id)

            self._log_action(
                f"Request {request_id} completed",
                {'technician_id': technician_id, 'hours': actual_hours}
            )

            # Publish REQUEST_COMPLETED event
            self.event_bus.publish(
                EventTypes.REQUEST_COMPLETED,
                {
                    'request_id': request_id,
                    'technician_id': technician_id,
                    'asset_id': request.asset_id,
                    'completion_notes': completion_notes,
                    'actual_hours': actual_hours
                },
                source='MaintenanceService.complete_request'
            )

            # Notify submitter
            self.notification_service.notify_user(
                user_id=request.submitter_id,
                subject=f"Completed: {request.title}",
                message=f"Your maintenance request #{request.id} has been completed. "
                       f"Notes: {completion_notes}"
            )

            # Notify admins
            self.notification_service.notify_by_role(
                role='admin',
                subject=f"Request Completed: #{request.id}",
                message=f"Maintenance request #{request.id} completed by technician. "
                       f"Hours: {actual_hours or 'N/A'}"
            )

            return self._build_success_response(
                data=updated_request.to_dict(),
                message="Request completed successfully"
            )

        except ValueError as e:
            return self._build_error_response(str(e))
        except Exception as e:
            return self._handle_exception(e, "complete_request")

    def get_technician_workload(self, technician_id: int) -> dict:
        """Get workload metrics for a technician."""
        try:
            workload = self.request_repo.get_technician_workload(technician_id)
            return self._build_success_response(data=workload)
        except Exception as e:
            return self._handle_exception(e, "get_technician_workload")

    def get_unassigned_requests(self) -> dict:
        """Get all unassigned requests for admin dashboard."""
        try:
            requests = self.request_repo.get_unassigned_requests()
            return self._build_success_response(
                data=[req.to_dict() for req in requests],
                message=f"Found {len(requests)} unassigned requests"
            )
        except Exception as e:
            return self._handle_exception(e, "get_unassigned_requests")

    def _notify_admins_new_request(self, request, submitter, asset) -> None:
        """Helper: Notify admins of new request."""
        try:
            asset_name = asset.name if asset else "No specific asset"
            self.notification_service.notify_by_role(
                role='admin',
                subject=f"New Maintenance Request: {request.title}",
                message=f"New {request.type} request submitted by {submitter.full_name}. "
                       f"Priority: {request.priority.value.upper()}. Asset: {asset_name}. "
                       f"Request ID: #{request.id}"
            )
        except Exception as e:
            self._log_action(f"Failed to notify admins: {str(e)}")
