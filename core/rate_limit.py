from fastapi import HTTPException
from collections import defaultdict
from datetime import date

DAILY_LIMIT = 10
_request_counts: dict = defaultdict(lambda: defaultdict(int))


def check_rate_limit(ip: str):
    today = str(date.today())
    _request_counts[ip][today] += 1
    if _request_counts[ip][today] > DAILY_LIMIT:
        raise HTTPException(
            status_code=429,
            detail=f"Limite de {DAILY_LIMIT} analyses par jour atteinte. Revenez demain.",
        )
