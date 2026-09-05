"""Расчеты для экзаменационной задачи №2."""
from __future__ import annotations

import math
from typing import Iterable


def critical_mass(arpu: float, maintenance: float, cac: float, reference_new_users: float) -> float:
    """Return N where revenue covers maintenance and a reference CAC bill."""
    return (maintenance + cac * reference_new_users) / arpu


def users_path(initial: float, growth_before: float, growth_after: float, critical: float, horizon: int) -> list[float]:
    users = [float(initial)]
    reached = False
    for _ in range(horizon):
        rate = growth_after if reached else growth_before
        next_users = min(users[-1] * (1 + rate), 1_000_000)
        if not reached and next_users >= critical:
            reached = True
        users.append(next_users)
    return users


def cash_flow_table(users: Iterable[float], arpu: float, maintenance: float, cac: float) -> list[dict[str, float]]:
    rows = []
    previous = 0.0
    for month, current in enumerate(users):
        new_users = max(current - previous, 0.0)
        revenue = arpu * current
        acquisition = cac * new_users
        profit = revenue - maintenance - acquisition
        rows.append({
            "month": month,
            "users": current,
            "new_users": new_users,
            "revenue": revenue,
            "maintenance": maintenance,
            "acquisition_cost": acquisition,
            "profit": profit,
        })
        previous = current
    return rows


def npv(monthly_cash_flows: Iterable[float], rate: float) -> float:
    return sum(cf / ((1 + rate) ** month) for month, cf in enumerate(monthly_cash_flows, start=1))


def break_even_arpu(users: Iterable[float], maintenance: float, cac: float, rate: float = 0.01) -> float:
    user_list = list(users)
    weights = []
    for month, (current, previous) in enumerate(zip(user_list[1:], user_list[:-1]), start=1):
        new_users = max(current - previous, 0.0)
        discount = (1 + rate) ** month
        weights.append((current / discount, new_users / discount))
    total_users_pv = sum(x for x, _ in weights)
    total_cost_pv = sum(maintenance / ((1 + rate) ** month) + cac * y for month, (_, y) in enumerate(weights, start=1))
    return total_cost_pv / total_users_pv if total_users_pv else math.inf
