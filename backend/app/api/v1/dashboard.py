from __future__ import annotations

from fastapi import APIRouter

from app.db.store import store
from app.schemas.common import DashboardSummary

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/summary", response_model=DashboardSummary)
async def dashboard_summary():
    return {**store.summary(), "patients": store.roster()}
