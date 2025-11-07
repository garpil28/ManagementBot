import asyncio, os, sys
from datetime import datetime, timedelta
from utils.backup import create_backup_zip
from utils.timezone import WIB, now_wib_iso
from config import BACKUP_HOUR, BACKUP_MINUTE, AUTO_RESTART_HOUR, AUTO_RESTART_MINUTE

def _seconds_until(hour, minute):
    now = datetime.now(WIB)
    target = datetime(now.year, now.month, now.day, hour, minute, tzinfo=WIB)
    if target <= now:
        target = target + timedelta(days=1)
    return (target - now).total_seconds()

async def _backup_loop():
    while True:
        secs = _seconds_until(BACKUP_HOUR, BACKUP_MINUTE)
        await asyncio.sleep(secs)
        try:
            file = create_backup_zip(['data', 'backups'], prefix='daily_backup')
            print("[scheduler] backup created", file)
        except Exception as e:
            print("[scheduler] backup error", e)
        await asyncio.sleep(1)

async def _restart_loop():
    while True:
        secs = _seconds_until(AUTO_RESTART_HOUR, AUTO_RESTART_MINUTE)
        await asyncio.sleep(secs)
        try:
            file = create_backup_zip(['data', 'backups'], prefix='pre_restart')
            print("[scheduler] pre-restart backup", file)
        except Exception as e:
            print("[scheduler] pre-restart backup failed", e)
        os.execv(sys.executable, [sys.executable] + sys.argv)

def start_scheduler(loop):
    loop.create_task(_backup_loop())
    loop.create_task(_restart_loop())
