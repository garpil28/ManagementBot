# data/__init__.py — Garfield Bot Data Package
"""
Modul ini menandai folder /data sebagai package Python.

Berisi:
- database.py   → koneksi dan fungsi MongoDB
- backup_utils.py → fungsi backup otomatis ke zip harian
"""

from .database import *
from .backup_utils import *
