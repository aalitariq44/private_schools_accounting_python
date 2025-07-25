# إعدادات التطبيق العامة
import os
from pathlib import Path

# مسارات المشروع
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_DIR = DATA_DIR / "database"
UPLOADS_DIR = DATA_DIR / "uploads"
BACKUPS_DIR = DATA_DIR / "backups"
EXPORTS_DIR = DATA_DIR / "exports"
LOGS_DIR = BASE_DIR / "logs"
RESOURCES_DIR = BASE_DIR / "resources"

# إعدادات قاعدة البيانات
DATABASE_NAME = "schools.db"
DATABASE_PATH = DATABASE_DIR / DATABASE_NAME

# إعدادات التطبيق
APP_NAME = "حسابات المدارس الأهلية"
APP_VERSION = "1.0.0"
APP_ORGANIZATION = "Private Schools Solutions"

# إعدادات النافذة
WINDOW_TITLE = f"{APP_NAME} - الإصدار {APP_VERSION}"
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 800

# إعدادات الأمان
PASSWORD_MIN_LENGTH = 6
SESSION_TIMEOUT = 3600  # ساعة واحدة بالثواني

# إعدادات النسخ الاحتياطي
BACKUP_INTERVAL_DAYS = 7
MAX_BACKUP_FILES = 30

# إنشاء المجلدات المطلوبة
for directory in [DATA_DIR, DATABASE_DIR, UPLOADS_DIR, BACKUPS_DIR, EXPORTS_DIR, LOGS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# إنشاء مجلدات فرعية للرفوعات
(UPLOADS_DIR / "school_logos").mkdir(exist_ok=True)
(UPLOADS_DIR / "temp").mkdir(exist_ok=True)

# إنشاء مجلدات فرعية للنسخ الاحتياطية
(BACKUPS_DIR / "daily").mkdir(exist_ok=True)
(BACKUPS_DIR / "weekly").mkdir(exist_ok=True)
(BACKUPS_DIR / "manual").mkdir(exist_ok=True)

# إنشاء مجلدات فرعية للصادرات
(EXPORTS_DIR / "reports").mkdir(exist_ok=True)
(EXPORTS_DIR / "prints").mkdir(exist_ok=True)

# وضع التطوير (True لتفعيل وضع التطوير، False للإنتاج)
DEBUG_MODE = True
