"""
Event Type Constants

Centralized definition of all application event types.
This ensures consistency across the system and makes it easy to
discover all available events.
"""


class EventTypes:
    """
    Application event type constants.

    Events are organized by domain:
    - Request Events: Maintenance request lifecycle
    - Asset Events: Asset management and tracking
    - User Events: Authentication and user management
    """

    # ========================================
    # Request Lifecycle Events
    # ========================================

    REQUEST_CREATED = "REQUEST_CREATED"
    """
    Triggered when a new maintenance request is created.

    Data:
        - request_id: int
        - type: str (electrical, plumbing, hvac)
        - priority: str (low, medium, high, urgent)
        - submitter_id: int
        - asset_id: int
    """

    REQUEST_ASSIGNED = "REQUEST_ASSIGNED"
    """
    Triggered when a request is assigned to a technician.

    Data:
        - request_id: int
        - technician_id: int
        - asset_id: int
        - assigned_by_id: int
    """

    REQUEST_STARTED = "REQUEST_STARTED"
    """
    Triggered when a technician starts working on a request.

    Data:
        - request_id: int
        - technician_id: int
        - started_at: datetime
    """

    REQUEST_COMPLETED = "REQUEST_COMPLETED"
    """
    Triggered when a request is marked as completed.

    Data:
        - request_id: int
        - technician_id: int
        - completed_at: datetime
        - completion_notes: str
        - hours_worked: float
    """

    REQUEST_CANCELLED = "REQUEST_CANCELLED"
    """
    Triggered when a request is cancelled.

    Data:
        - request_id: int
        - cancelled_by_id: int
        - reason: str
    """

    REQUEST_STATUS_CHANGED = "REQUEST_STATUS_CHANGED"
    """
    Triggered when request status changes.

    Data:
        - request_id: int
        - old_status: str
        - new_status: str
        - changed_by_id: int
    """

    # ========================================
    # Asset Events
    # ========================================

    ASSET_CREATED = "ASSET_CREATED"
    """
    Triggered when a new asset is registered.

    Data:
        - asset_id: int
        - name: str
        - category: str
        - created_by_id: int
    """

    ASSET_CONDITION_CHANGED = "ASSET_CONDITION_CHANGED"
    """
    Triggered when asset condition is updated.

    Data:
        - asset_id: int
        - old_condition: str
        - new_condition: str
        - changed_by_id: int
    """

    ASSET_STATUS_CHANGED = "ASSET_STATUS_CHANGED"
    """
    Triggered when asset status changes.

    Data:
        - asset_id: int
        - old_status: str
        - new_status: str
        - reason: str
    """

    ASSET_RETIRED = "ASSET_RETIRED"
    """
    Triggered when an asset is retired.

    Data:
        - asset_id: int
        - retired_by_id: int
        - reason: str
    """

    ASSET_ASSIGNED_TO_REQUEST = "ASSET_ASSIGNED_TO_REQUEST"
    """
    Triggered when asset is linked to a maintenance request.

    Data:
        - asset_id: int
        - request_id: int
    """

    # ========================================
    # User Events
    # ========================================

    USER_REGISTERED = "USER_REGISTERED"
    """
    Triggered when a new user registers.

    Data:
        - user_id: int
        - email: str
        - role: str
    """

    USER_LOGIN = "USER_LOGIN"
    """
    Triggered when a user logs in.

    Data:
        - user_id: int
        - email: str
        - ip_address: str (optional)
    """

    USER_LOGOUT = "USER_LOGOUT"
    """
    Triggered when a user logs out.

    Data:
        - user_id: int
    """

    USER_PASSWORD_CHANGED = "USER_PASSWORD_CHANGED"
    """
    Triggered when user changes password.

    Data:
        - user_id: int
    """

    TECHNICIAN_ASSIGNED = "TECHNICIAN_ASSIGNED"
    """
    Triggered when technician is assigned to request (for metrics).

    Data:
        - technician_id: int
        - request_id: int
        - workload_count: int
    """

    # ========================================
    # System Events
    # ========================================

    SYSTEM_ERROR = "SYSTEM_ERROR"
    """
    Triggered when a system error occurs.

    Data:
        - error_type: str
        - message: str
        - stack_trace: str (optional)
    """

    @classmethod
    def all_events(cls) -> list:
        """
        Get list of all event types.

        Returns:
            List of all event type constants
        """
        return [
            value for name, value in vars(cls).items()
            if isinstance(value, str) and name.isupper()
        ]

    @classmethod
    def request_events(cls) -> list:
        """Get all request-related events."""
        return [
            cls.REQUEST_CREATED,
            cls.REQUEST_ASSIGNED,
            cls.REQUEST_STARTED,
            cls.REQUEST_COMPLETED,
            cls.REQUEST_CANCELLED,
            cls.REQUEST_STATUS_CHANGED,
        ]

    @classmethod
    def asset_events(cls) -> list:
        """Get all asset-related events."""
        return [
            cls.ASSET_CREATED,
            cls.ASSET_CONDITION_CHANGED,
            cls.ASSET_STATUS_CHANGED,
            cls.ASSET_RETIRED,
            cls.ASSET_ASSIGNED_TO_REQUEST,
        ]

    @classmethod
    def user_events(cls) -> list:
        """Get all user-related events."""
        return [
            cls.USER_REGISTERED,
            cls.USER_LOGIN,
            cls.USER_LOGOUT,
            cls.USER_PASSWORD_CHANGED,
            cls.TECHNICIAN_ASSIGNED,
        ]
