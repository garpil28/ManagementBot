# data/backup_utils.py — Garfield Bot Backup Utility
import os
import zipfile
from datetime import datetime
from pytz import timezone
import logging


def ensure_dir(path: str):
    """Buat folder jika belum ada."""
    if not os.path.exists(path):
        os.makedirs(path)


async def daily_backup():
    """
    Buat backup harian otomatis untuk folder data penting.
    Hasil file: backups/backup_YYYYMMDD_HHMM.zip
    """
    try:
        # Lokasi penyimpanan backup
        now = datetime.now(timezone("Asia/Jakarta")).strftime("%Y%m%d_%H%M")
        backup_dir = "backups"
        ensure_dir(backup_dir)

        # Nama file zip
        zip_name = f"backup_{now}.zip"
        zip_path = os.path.join(backup_dir, zip_name)

        # Folder yang ingin di-backup (bisa ubah sesuai kebutuhan)
        folders_to_backup = ["data"]

        # Proses zip
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as backup_zip:
            for folder in folders_to_backup:
                for root, _, files in os.walk(folder):
                    for file in files:
                        file_path = os.path.join(root, file)
                        arcname = os.path.relpath(file_path, folder)
                        backup_zip.write(file_path, os.path.join(folder, arcname))

        logging.info(f"💾 Backup berhasil dibuat: {zip_path}")
        return zip_path

    except Exception as e:
        logging.error(f"⚠️ Gagal membuat backup: {e}")
        return None
