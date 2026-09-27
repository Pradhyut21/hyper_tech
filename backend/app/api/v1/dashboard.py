from __future__ import annotations

from fastapi import APIRouter

from app.db.store import store

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard/summary")
async def dashboard_summary():
    return {**store.summary(), "patients": store.roster()}
