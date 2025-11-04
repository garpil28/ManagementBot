# utils/backup.py — backups (zip) for data folder or selective dump
import os
import zipfile
from pathlib import Path
from utils.timezone import now_wib_str
from db.mongo import backups_col

BACKUP_ROOT = Path(os.getenv('BACKUP_FOLDER', 'backups'))
BACKUP_ROOT.mkdir(parents=True, exist_ok=True)


def create_backup_zip(src_paths, prefix='backup'):
    ts = now_wib_str()
    name = f"{prefix}_{ts}.zip"
    dest = BACKUP_ROOT / name
    with zipfile.ZipFile(dest, 'w', zipfile.ZIP_DEFLATED) as zf:
        for p in src_paths:
            p = Path(p)
            if p.is_dir():
                for f in p.rglob('*'):
                    zf.write(f, arcname=f.relative_to(p.parent))
            elif p.is_file():
                zf.write(p, arcname=p.name)
    # record in DB
    backups_col.insert_one({'file': str(dest), 'created_at': now_wib_str(), 'note': prefix})
    return str(dest)
