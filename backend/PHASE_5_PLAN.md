# Phase 5 Implementation Plan
## Event-Driven Architecture with Observer Pattern

**Date:** November 8, 2025
**Status:** 📋 PLANNING
**Phase:** 5 of 7 (Following Roadmap Phase 3)
**Estimated Duration:** 2-3 days

---

## 🎯 Phase Objectives

### Primary Goals
- Implement Observer Pattern for event notification
- Create EventBus singleton for centralized event management
- Decouple components through event-driven architecture
- Add reactive behavior to system state changes
- Demonstrate Open/Closed Principle through extensible observers

### Success Criteria
- [ ] Observer pattern implemented (Subject/Observer base classes)
- [ ] EventBus singleton created and integrated
- [ ] 4+ observer implementations working
- [ ] Services publish events on state changes
- [ ] Observers execute automatically on events
- [ ] Failed observers don't break other observers
- [ ] Event history logged with timestamps
- [ ] 80%+ test coverage for event system
- [ ] Integration tests verify event flow

---

## 📋 Current State Analysis

### What We Have ✅
- **Strategy Pattern:** NotificationService with Email/SMS/InApp strategies
- **Service Layer:** MaintenanceService, UserService, AssetService
- **Direct Coupling:** Services call NotificationService directly
- **No Event System:** No decoupled event handling

### What's Missing ❌
- **Observer Pattern:** No Subject/Observer abstraction
- **EventBus:** No centralized event dispatcher
- **Event Publishing:** Services don't publish domain events
- **Multiple Observers:** Only notification happens, no logging/metrics/audit
- **Event History:** No record of system events

### Current Notification Flow
```
Service → NotificationService → Strategy (Email/SMS/InApp)
```

### Target Event-Driven Flow
```
Service → EventBus → [NotificationObserver, LoggingObserver, MetricsObserver, AuditObserver]
           ↓
      Event History
```

---

## 🏗️ Architecture Design

### Observer Pattern Structure

```python
# Pattern Components:
1. Subject (EventBus) - Manages observers, publishes events
2. Observer (Abstract) - Interface for all observers
3. Concrete Observers - NotificationObserver, LoggingObserver, etc.
4. Event - Data container with type, data, timestamp
```

### Class Diagram
```
┌─────────────────────────┐
│      EventBus           │
│    (Singleton)          │
├─────────────────────────┤
│ + subscribe(event, obs) │
│ + publish(event, data)  │
│ + get_history()         │
└────────────┬────────────┘
             │ notifies
             ↓
      ┌─────────────┐
      │  Observer   │ (Abstract)
      │  (ABC)      │
      ├─────────────┤
      │ + update()  │
      └──────┬──────┘
             │ implements
    ┌────────┴────────┬──────────────┬─────────────────┐
    ↓                 ↓              ↓                 ↓
┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│Notification │ │  Logging    │ │  Metrics    │ │ AssetStatus │
│Observer     │ │  Observer   │ │  Observer   │ │ Observer    │
└─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘
```

---

## 📦 Implementation Plan

### Step 1: Core Observer Pattern (1-2 hours)

**Files to Create:**
1. `app/patterns/observer.py` - Observer pattern base classes

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Any
from datetime import datetime

class Event:
    """Domain event with type, data, and metadata."""
    def __init__(self, event_type: str, data: Dict[str, Any], source: str = None):
        self.event_type = event_type
        self.data = data
        self.source = source
        self.timestamp = datetime.utcnow()
        self.event_id = generate_event_id()

class Observer(ABC):
    """Abstract observer that responds to events."""

    @abstractmethod
    def update(self, event: Event) -> None:
        """Handle event notification."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Observer name for logging."""
        pass

class Subject:
    """Base subject that manages observers."""

    def __init__(self):
        self._observers: Dict[str, List[Observer]] = {}

    def attach(self, event_type: str, observer: Observer) -> None:
        """Attach observer to specific event type."""
        pass

    def detach(self, event_type: str, observer: Observer) -> None:
        """Detach observer from event type."""
        pass

    def notify(self, event: Event) -> None:
        """Notify all observers of event."""
        pass
```

**Deliverables:**
- [ ] Event class with type, data, timestamp
- [ ] Observer abstract base class
- [ ] Subject base class with attach/detach/notify
- [ ] Unit tests for observer pattern

---

### Step 2: EventBus Singleton (1-2 hours)

**Files to Create:**
1. `app/patterns/event_bus.py` - Centralized event dispatcher

```python
from app.patterns.singleton import Singleton
from app.patterns.observer import Subject, Event, Observer

class EventBus(Subject, metaclass=Singleton):
    """Centralized event bus for application-wide events."""

    def __init__(self):
        super().__init__()
        self._event_history: List[Event] = []
        self._max_history_size = 1000

    def publish(self, event_type: str, data: Dict[str, Any], source: str = None) -> Event:
        """Publish event to all subscribed observers."""
        event = Event(event_type, data, source)
        self._add_to_history(event)
        self.notify(event)
        return event

    def subscribe(self, event_type: str, observer: Observer) -> None:
        """Subscribe observer to event type."""
        self.attach(event_type, observer)

    def unsubscribe(self, event_type: str, observer: Observer) -> None:
        """Unsubscribe observer from event type."""
        self.detach(event_type, observer)

    def get_history(self, event_type: str = None, limit: int = 100) -> List[Event]:
        """Get event history."""
        pass

    def clear_history(self) -> None:
        """Clear event history."""
        pass
```

**Features:**
- Singleton pattern ensures one event bus
- Event history with configurable max size
- Subscribe/unsubscribe methods
- Query history by event type
- Automatic event timestamping

**Deliverables:**
- [ ] EventBus singleton implementation
- [ ] Event history storage
- [ ] Subscribe/unsubscribe functionality
- [ ] History query methods
- [ ] Unit tests for EventBus

---

### Step 3: Observer Implementations (2-3 hours)

**Files to Create:**
1. `app/observers/__init__.py`
2. `app/observers/notification_observer.py`
3. `app/observers/logging_observer.py`
4. `app/observers/metrics_observer.py`
5. `app/observers/asset_status_observer.py`

#### 3.1 NotificationObserver
```python
class NotificationObserver(Observer):
    """Triggers notifications via NotificationService."""

    def __init__(self, notification_service: NotificationService):
        self.notification_service = notification_service

    def update(self, event: Event) -> None:
        """Handle event and trigger appropriate notification."""
        if event.event_type == 'REQUEST_CREATED':
            self._notify_request_created(event.data)
        elif event.event_type == 'REQUEST_ASSIGNED':
            self._notify_request_assigned(event.data)
        elif event.event_type == 'REQUEST_COMPLETED':
            self._notify_request_completed(event.data)
```

#### 3.2 LoggingObserver
```python
class LoggingObserver(Observer):
    """Logs all events to file/database."""

    def update(self, event: Event) -> None:
        """Log event with details."""
        logger.info(f"[{event.event_type}] {event.data}")
```

#### 3.3 MetricsObserver
```python
class MetricsObserver(Observer):
    """Tracks KPIs and metrics."""

    def update(self, event: Event) -> None:
        """Update metrics based on event."""
        if event.event_type == 'REQUEST_COMPLETED':
            self._track_completion_time(event.data)
            self._update_technician_stats(event.data)
```

#### 3.4 AssetStatusObserver
```python
class AssetStatusObserver(Observer):
    """Auto-updates asset status based on events."""

    def update(self, event: Event) -> None:
        """Update asset status."""
        if event.event_type == 'REQUEST_ASSIGNED':
            self._mark_asset_in_maintenance(event.data['asset_id'])
        elif event.event_type == 'REQUEST_COMPLETED':
            self._restore_asset_status(event.data['asset_id'])
```

**Deliverables:**
- [ ] 4 concrete observer implementations
- [ ] Error handling in each observer
- [ ] Unit tests for each observer
- [ ] Integration tests for observer behavior

---

### Step 4: Event Types Definition (30 minutes)

**Files to Create:**
1. `app/events/__init__.py`
2. `app/events/event_types.py` - Centralized event type constants

```python
class EventTypes:
    """Application event type constants."""

    # Request Events
    REQUEST_CREATED = "REQUEST_CREATED"
    REQUEST_ASSIGNED = "REQUEST_ASSIGNED"
    REQUEST_STARTED = "REQUEST_STARTED"
    REQUEST_COMPLETED = "REQUEST_COMPLETED"
    REQUEST_CANCELLED = "REQUEST_CANCELLED"
    REQUEST_STATUS_CHANGED = "REQUEST_STATUS_CHANGED"

    # Asset Events
    ASSET_CREATED = "ASSET_CREATED"
    ASSET_CONDITION_CHANGED = "ASSET_CONDITION_CHANGED"
    ASSET_RETIRED = "ASSET_RETIRED"
    ASSET_ASSIGNED_TO_REQUEST = "ASSET_ASSIGNED_TO_REQUEST"

    # User Events
    USER_REGISTERED = "USER_REGISTERED"
    USER_LOGIN = "USER_LOGIN"
    USER_LOGOUT = "USER_LOGOUT"
    TECHNICIAN_ASSIGNED = "TECHNICIAN_ASSIGNED"
```

**Deliverables:**
- [ ] Event type constants
- [ ] Event documentation
- [ ] Type hints for events

---

### Step 5: Service Integration (2-3 hours)

**Files to Modify:**
1. `app/services/maintenance_service.py`
2. `app/services/user_service.py`
3. `app/services/asset_service.py`

#### Example: MaintenanceService Integration
```python
from app.patterns.event_bus import EventBus
from app.events.event_types import EventTypes

class MaintenanceService(BaseService):
    def __init__(self, request_repo, asset_repo, user_repo):
        super().__init__()
        self.request_repo = request_repo
        self.asset_repo = asset_repo
        self.user_repo = user_repo
        self.event_bus = EventBus()  # Get singleton instance

    def create_request(self, data: dict) -> dict:
        """Create request and publish event."""
        # Create request
        request = self._create_request_internal(data)

        # Publish event
        self.event_bus.publish(
            EventTypes.REQUEST_CREATED,
            {
                'request_id': request.id,
                'type': request.type,
                'priority': request.priority,
                'submitter_id': request.submitted_by_id,
                'asset_id': request.asset_id
            },
            source='MaintenanceService.create_request'
        )

        return self._build_success_response(data=request.to_dict())

    def assign_technician(self, request_id: int, technician_id: int) -> dict:
        """Assign technician and publish event."""
        # Assign technician
        request = self._assign_technician_internal(request_id, technician_id)

        # Publish event
        self.event_bus.publish(
            EventTypes.REQUEST_ASSIGNED,
            {
                'request_id': request_id,
                'technician_id': technician_id,
                'asset_id': request.asset_id
            },
            source='MaintenanceService.assign_technician'
        )

        return self._build_success_response(data=request.to_dict())
```

**Integration Points:**
- Request lifecycle events
- Asset condition changes
- User authentication events
- Status transitions

**Deliverables:**
- [ ] Event publishing in MaintenanceService
- [ ] Event publishing in AssetService
- [ ] Event publishing in UserService
- [ ] Integration tests for event flow

---

### Step 6: Observer Registration (1 hour)

**Files to Modify:**
1. `app/__init__.py` - Register observers on app startup

```python
def create_app(config_name='development'):
    app = Flask(__name__)
    # ... existing setup ...

    # Initialize event system
    with app.app_context():
        _register_observers()

    return app

def _register_observers():
    """Register all observers with EventBus."""
    from app.patterns.event_bus import EventBus
    from app.observers import (
        NotificationObserver,
        LoggingObserver,
        MetricsObserver,
        AssetStatusObserver
    )
    from app.services import NotificationService
    from app.events.event_types import EventTypes

    event_bus = EventBus()

    # Initialize services
    notification_service = NotificationService(...)

    # Create observers
    notification_obs = NotificationObserver(notification_service)
    logging_obs = LoggingObserver()
    metrics_obs = MetricsObserver()
    asset_status_obs = AssetStatusObserver()

    # Subscribe to events
    event_bus.subscribe(EventTypes.REQUEST_CREATED, notification_obs)
    event_bus.subscribe(EventTypes.REQUEST_CREATED, logging_obs)
    event_bus.subscribe(EventTypes.REQUEST_CREATED, metrics_obs)

    event_bus.subscribe(EventTypes.REQUEST_ASSIGNED, notification_obs)
    event_bus.subscribe(EventTypes.REQUEST_ASSIGNED, logging_obs)
    event_bus.subscribe(EventTypes.REQUEST_ASSIGNED, asset_status_obs)

    # ... register more subscriptions ...
```

**Deliverables:**
- [ ] Observer registration function
- [ ] App initialization integration
- [ ] Configuration for enabling/disabling observers
- [ ] Verification that observers execute

---

### Step 7: Testing (2-3 hours)

**Files to Create:**
1. `tests/unit/test_observer_pattern.py`
2. `tests/unit/test_event_bus.py`
3. `tests/unit/test_observers.py`
4. `tests/integration/test_event_flow.py`

#### Unit Tests
```python
# Test observer pattern
def test_observer_receives_notification()
def test_multiple_observers_notified()
def test_observer_can_unsubscribe()
def test_failed_observer_doesnt_break_others()

# Test EventBus
def test_event_bus_is_singleton()
def test_event_history_stored()
def test_event_history_query()
def test_event_history_max_size()

# Test observers
def test_notification_observer_triggers_notification()
def test_logging_observer_logs_event()
def test_metrics_observer_updates_stats()
def test_asset_status_observer_updates_asset()
```

#### Integration Tests
```python
def test_request_creation_triggers_all_observers()
def test_request_assignment_notifies_technician()
def test_request_completion_updates_metrics()
def test_asset_condition_change_logged()
```

**Deliverables:**
- [ ] 20+ unit tests for event system
- [ ] 10+ integration tests for event flow
- [ ] 80%+ code coverage for observers
- [ ] Error handling tests

---

## 📊 Event Mapping

### Request Events
| Event | Triggers | Observers |
|-------|----------|-----------|
| REQUEST_CREATED | Service creates request | Notification, Logging, Metrics |
| REQUEST_ASSIGNED | Admin assigns technician | Notification, Logging, AssetStatus |
| REQUEST_STARTED | Technician starts work | Notification, Logging, Metrics |
| REQUEST_COMPLETED | Technician completes | Notification, Logging, Metrics, AssetStatus |
| REQUEST_STATUS_CHANGED | Any status change | Notification, Logging |

### Asset Events
| Event | Triggers | Observers |
|-------|----------|-----------|
| ASSET_CONDITION_CHANGED | Condition updated | Logging, Metrics |
| ASSET_RETIRED | Asset retired | Logging, Metrics |

### User Events
| Event | Triggers | Observers |
|-------|----------|-----------|
| USER_REGISTERED | New user signs up | Notification, Logging |
| TECHNICIAN_ASSIGNED | Technician gets request | Metrics |

---

## 🎯 OOP Principles Demonstrated

### Open/Closed Principle ✅
- Adding new observers doesn't modify existing code
- New event types don't require changing EventBus

### Single Responsibility Principle ✅
- Each observer handles one concern (notification, logging, metrics)
- EventBus only manages event distribution

### Dependency Inversion Principle ✅
- Services depend on EventBus abstraction, not concrete observers
- Observers depend on Observer interface

### Loose Coupling ✅
- Services don't know about observers
- Observers don't know about each other
- EventBus mediates all communication

---

## ✅ Verification Checklist

### Pattern Implementation
- [ ] Observer abstract class defined
- [ ] Subject base class defined
- [ ] Event class with metadata
- [ ] EventBus singleton working
- [ ] 4+ concrete observers implemented

### Integration
- [ ] Services publish events on state changes
- [ ] Observers registered on app startup
- [ ] Events flow from service → EventBus → observers
- [ ] Failed observer doesn't break others

### Testing
- [ ] Unit tests for observer pattern (95%+ coverage)
- [ ] Unit tests for each observer
- [ ] Integration tests for event flow
- [ ] Error handling tested
- [ ] Event history query tested

### Documentation
- [ ] Event types documented
- [ ] Observer pattern explained
- [ ] Integration guide written
- [ ] PHASE_5_SUMMARY.md created

---

## 📈 Success Metrics

### Code Quality
- **Target:** 80%+ code coverage for event system
- **Target:** 100% test pass rate maintained
- **Target:** Zero breaking changes to existing tests

### Functionality
- **Target:** 10+ event types implemented
- **Target:** 4+ observers working
- **Target:** Events logged with <1ms overhead
- **Target:** Failed observers isolated (no cascade failures)

### Architecture
- **Target:** Services decoupled from observers
- **Target:** New observers added without code changes
- **Target:** Event history queryable

---

## 🚀 Next Steps After Phase 5

1. **Phase 6 (Roadmap):** Integration & Advanced Features
   - Analytics dashboard
   - Caching layer
   - Audit trail

2. **Phase 5 (Roadmap):** Blazor Frontend Foundation
   - Build UI consuming event-driven backend
   - Real-time updates via EventBus

3. **Phase 7:** Testing & Documentation
   - Complete documentation
   - Deployment preparation

---

## 📝 Notes

### Why Event-Driven Architecture?
- **Extensibility:** Add features without modifying existing code
- **Testability:** Test components in isolation
- **Maintainability:** Clear separation of concerns
- **Scalability:** Easy to add async processing later

### Current vs. Future
**Current (Direct Coupling):**
```python
def create_request(data):
    request = repo.create(data)
    notification_service.notify(...)  # Tightly coupled
    return request
```

**Future (Event-Driven):**
```python
def create_request(data):
    request = repo.create(data)
    event_bus.publish('REQUEST_CREATED', {...})  # Decoupled
    return request
```

---

*Created: November 8, 2025*
*Smart Maintenance Management System*
*Phase 5: Event-Driven Architecture with Observer Pattern*
