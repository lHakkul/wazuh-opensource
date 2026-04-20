import uuid
from collections import deque
from datetime import datetime, timedelta
from typing import List
from app.models.schemas import HistoryEvent, HealthStatus
from app.config import settings

_events: deque = deque(maxlen=settings.HISTORY_MAX_EVENTS)


def add_event(
    event_type: str,
    severity: HealthStatus,
    component: str,
    message: str,
    details: dict = None,
) -> HistoryEvent:
    event = HistoryEvent(
        id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        event_type=event_type,
        severity=severity,
        component=component,
        message=message,
        details=details,
    )
    _events.appendleft(event)
    return event


def get_events(limit: int = 50) -> List[HistoryEvent]:
    return list(_events)[:limit]


def get_events_since(hours: int) -> List[HistoryEvent]:
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    return [event for event in _events if event.timestamp >= cutoff]


def clear_events():
    _events.clear()
