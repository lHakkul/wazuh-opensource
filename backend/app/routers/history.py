import uuid
from fastapi import APIRouter, Query
from app.config import settings
from app.services import history
from app.models.schemas import HistoryEvent, HealthStatus
from datetime import datetime, timedelta
from typing import List

router = APIRouter(prefix="/api/history", tags=["history"])

_mock_seeded = False


def _seed_mock_history():
    global _mock_seeded
    if _mock_seeded:
        return
    from app.services.mock import MOCK_HISTORY
    for ev in reversed(MOCK_HISTORY):
        history.add_event(
            event_type=ev["event_type"],
            severity=HealthStatus(ev["severity"]),
            component=ev["component"],
            message=ev["message"],
        )
    _mock_seeded = True


@router.get("", response_model=List[HistoryEvent])
async def get_history(limit: int = Query(50, ge=1, le=200)):
    if settings.WAZUH_MOCK:
        _seed_mock_history()
    return history.get_events(limit=limit)


@router.delete("")
async def clear_history():
    global _mock_seeded
    history.clear_events()
    _mock_seeded = False
    return {"message": "Historial limpiado"}
