import time
from collections import defaultdict

MAX_ATTEMPTS = 5
WINDOW_SECONDS = 60  # 1 minute

_attempts = defaultdict(list)


def check_rate_limit(key: str) -> bool:
    """
    Returns False if rate limit exceeded.
    Auto-resets after WINDOW_SECONDS.
    """
    now = time.time()

    # keep only attempts within the time window
    _attempts[key] = [
        ts for ts in _attempts[key]
        if now - ts < WINDOW_SECONDS
    ]

    if len(_attempts[key]) >= MAX_ATTEMPTS:
        return False

    _attempts[key].append(now)
    return True
