# utils/scheduler.py — restart & backup schedule
import asyncio
import os
import sys
from utils.timezone import now_wib_iso, now_wib_str, WIB
from datetime import datetime, timedelta
from utils.backup import create_backup_zip
from db.mongo import backups_col, partners_col
from config import AUTO_RESTART_HOUR, AUTO_RESTART_MINUTE, BACKUP_HOUR, BACKUP_MINUTE, BACKUP_FOLDER
from pyrogram import Client

# run scheduler tasks inside event loop

def _seconds_until(hour, minute):
    now = datetime.now(WIB)
    target = datetime(now.year, now.month, now.day, hour, minute, tzinfo=WIB)
    if target <= now:
        target = target + timedelta(days=1)
    return (target - now).total_seconds()


def start_scheduler(loop):
    # schedule backup then restart at 00:00 WIB
    loop.create_task(_backup_loop())
    loop.create_task(_restart_loop())


async def _backup_loop():
    while True:
        secs = _seconds_until(BACKUP_HOUR, BACKUP_MINUTE)
        await asyncio.sleep(secs)
        # create backup of local data folder and record in db
        try:
            zipfile = create_backup_zip(['data', 'backups'], prefix='daily_backup')
            backups_col.insert_one({'path': zipfile, 'created_at': now_wib_iso()})
            print(f'[backup] created {zipfile}')
        except Exception as e:
            print('backup error', e)
        await asyncio.sleep(1)

async def _restart_loop():
    while True:
        secs = _seconds_until(AUTO_RESTART_HOUR, AUTO_RESTART_MINUTE)
        await asyncio.sleep(secs)
        print('[scheduler] Performing scheduled restart...')
        # create a backup immediately before restart
        try:
            zipfile = create_backup_zip(['data', 'backups'], prefix='pre_restart')
            backups_col.insert_one({'path': zipfile, 'created_at': now_wib_iso()})
        except Exception as e:
            print('pre-restart backup failed', e)
        # restart process
        os.execv(sys.executable, [sys.executable] + sys.argv)
