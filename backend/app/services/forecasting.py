"""Transparent demand projection from completed relief allocations and current inventory."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from math import ceil

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models import InventoryItem, ResourceAllocation

WINDOW_DAYS = 28

def forecast_demand(db: Session, horizon_days: int = 7) -> dict:
    now = datetime.now(timezone.utc)
    recent_start = now - timedelta(days=WINDOW_DAYS)
    previous_start = now - timedelta(days=WINDOW_DAYS * 2)
    allocations = db.execute(
        select(InventoryItem.category, ResourceAllocation.quantity, ResourceAllocation.created_at)
        .join(InventoryItem, InventoryItem.id == ResourceAllocation.item_id)
        .where(ResourceAllocation.status == "Delivered", ResourceAllocation.created_at >= previous_start)
    ).all()
    current_stock = {
        category: int(total or 0)
        for category, total in db.execute(
            select(InventoryItem.category, func.coalesce(func.sum(InventoryItem.quantity), 0))
            .group_by(InventoryItem.category)
        )
    }
    recent: dict[str, int] = {}
    previous: dict[str, int] = {}
    for category, quantity, created_at in allocations:
        target = recent if created_at and created_at >= recent_start else previous
        target[category] = target.get(category, 0) + int(quantity)
    categories = sorted(set(current_stock) | set(recent) | set(previous))
    rows = []
    for category in categories:
        used = recent.get(category, 0)
        older = previous.get(category, 0)
        daily = used / WINDOW_DAYS
        projected = ceil(daily * horizon_days)
        rows.append({
            "category": category,
            "delivered_recent_28d": used,
            "delivered_previous_28d": older,
            "average_delivered_per_day": round(daily, 2),
            "projected_demand": projected,
            "current_stock": current_stock.get(category, 0),
            "projected_gap": max(0, projected - current_stock.get(category, 0)),
            "trend_percent": round((used - older) * 100 / older, 1) if older else None,
        })
    return {
        "horizon_days": horizon_days,
        "generated_at": now,
        "history_window_days": WINDOW_DAYS,
        "items": rows,
        "method": "Mean daily delivered units during the latest 28 days multiplied by the selected horizon; compared with the preceding 28 days and current recorded stock.",
        "limitations": "A planning estimate only. It uses recorded Delivered allocations, not all unmet needs or population forecasts. Seeded training allocations may be included. It is not a validated forecast or an automatic purchase/dispatch order.",
    }
