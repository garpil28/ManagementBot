from datetime import datetime
import pytz

WIB = pytz.timezone("Asia/Jakarta")

def now_wib_str():
    return datetime.now(WIB).strftime("%Y-%m-%d %H:%M:%S")

def now_wib_iso():
    return datetime.now(WIB).isoformat()
