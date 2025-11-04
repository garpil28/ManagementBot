# utils/timezone.py — WIB helpers
from datetime import datetime, timezone, timedelta

WIB = timezone(timedelta(hours=7))

def now_wib_iso():
    return datetime.now(WIB).isoformat()

def now_wib_str(fmt="%Y%m%d_%H%M%S"):
    return datetime.now(WIB).strftime(fmt)
