import os, zipfile
from pathlib import Path
from utils.timezone import now_wib_str
from db.mongo import backups_col

BACKUP_ROOT = Path(os.getenv("BACKUP_FOLDER", "backups"))
BACKUP_ROOT.mkdir(exist_ok=True)

def create_backup_zip(src_paths, prefix="backup"):
    ts = now_wib_str()
    name = f"{prefix}_{ts}.zip"
    dest = BACKUP_ROOT / name

    with zipfile.ZipFile(dest, "w") as z:
        for p in src_paths:
            p = Path(p)
            if p.is_dir():
                for f in p.rglob("*"):
                    z.write(f, arcname=f.relative_to(p.parent))

    backups_col.insert_one({"file": str(dest), "created_at": ts})
    return str(dest)
