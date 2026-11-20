"""Расчеты для экзаменационной задачи №2."""
from __future__ import annotations
import math
from typing import Iterable


def critical_mass(arpu: float, maintenance: float, cac: float, reference_new_users: float) -> float:
    """Минимальная база пользователей, покрывающая поддержание и CAC."""
    return (maintenance + cac * reference_new_users) / arpu


def users_path(initial: float, growth_before: float, growth_after: float, critical: float, horizon: int, market_limit: float) -> list[float]:
    """Траектория пользователей с ограничением потенциалом рынка."""
    users = [float(initial)]
    reached = False
    for _ in range(horizon):
        rate = growth_after if reached else growth_before
        next_users = min(users[-1] * (1 + rate), market_limit)
        if not reached and next_users >= critical:
            reached = True
        users.append(next_users)
    return users


def cash_flow_table(users: Iterable[float], arpu: float, maintenance: float, cac: float) -> list[dict[str, float]]:
    """Помесячные денежные потоки; исходная база месяца 0 не считается новой."""
    user_list = list(users)
    rows = []
    previous = user_list[0] if user_list else 0.0
    for month, current in enumerate(user_list):
        new_users = 0.0 if month == 0 else max(current - previous, 0.0)
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
    """NPV потоков, начиная с месяца 1."""
    return sum(cf / ((1 + rate) ** month) for month, cf in enumerate(monthly_cash_flows, start=1))


def break_even_arpu(users: Iterable[float], maintenance: float, cac: float, rate: float = 0.01) -> float:
    """ARPU, при котором NPV помесячной модели равен нулю."""
    user_list = list(users)
    discounted_users = []
    discounted_costs = []
    for month, current in enumerate(user_list[1:], start=1):
        previous = user_list[month - 1]
        new_users = max(current - previous, 0.0)
        factor = (1 + rate) ** month
        discounted_users.append(current / factor)
        discounted_costs.append(maintenance / factor + cac * new_users / factor)
    total_users_pv = sum(discounted_users)
    return sum(discounted_costs) / total_users_pv if total_users_pv else math.inf
