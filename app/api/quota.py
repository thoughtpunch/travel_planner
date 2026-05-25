from fastapi import APIRouter

from ..config import settings
from ..db import get_session
from ..orchestrator.runner import _sum_used_serpapi_calls
from ..schemas import QuotaOut

router = APIRouter(prefix="/api/quota", tags=["quota"])


@router.get("", response_model=QuotaOut)
def quota_status():
    with get_session() as session:
        used = _sum_used_serpapi_calls(session)
    return QuotaOut(
        ceiling=settings.serpapi_monthly_ceiling,
        used_this_month=used,
        remaining=max(0, settings.serpapi_monthly_ceiling - used),
    )
