#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير النسخ الاحتياطية - Supabase Storage
يدير عمليات رفع وعرض النسخ الاحتياطية من قاعدة البيانات على Supabase
"""

import os
import shutil
import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import tempfile
import zipfile

try:
    from supabase import create_client
except ImportError:
    create_client = None
    logging.warning("supabase library not installed; backup functionality disabled.")
"""StorageException for handling storage errors; using generic Exception as fallback."""
StorageException = Exception

import config


class BackupManager:
    """مدير النسخ الاحتياطية"""
    
    def __init__(self):
        """تهيئة مدير النسخ الاحتياطية"""
        self.logger = logging.getLogger(__name__)
        # تحقق من توفر عميل Supabase
        if create_client is None:
            self.logger.error("Supabase client not available; backup functionality is disabled.")
            self.supabase = None
            return
        # تهيئة عميل Supabase
        self.supabase = create_client(config.SUPABASE_URL, config.SUPABASE_KEY)
        self.bucket_name = config.SUPABASE_BUCKET
        self.setup_storage()
    
    def setup_storage(self):
        """إعداد التخزين على Supabase"""
        try:
            # التحقق من وجود البكت أو إنشاؤه
            buckets = self.supabase.storage.list_buckets()
            bucket_exists = any(bucket.name == self.bucket_name for bucket in buckets)
            
            if not bucket_exists:
                self.supabase.storage.create_bucket(
                    self.bucket_name,
                    options={
                        "public": False,
                        "allowedMimeTypes": ["application/zip", "application/x-sqlite3"],
                        "fileSizeLimit": 100 * 1024 * 1024  # 100MB
                    }
                )
                self.logger.info(f"تم إنشاء بكت التخزين: {self.bucket_name}")
            else:
                self.logger.info(f"بكت التخزين موجود: {self.bucket_name}")
                
        except Exception as e:
            self.logger.error(f"خطأ في إعداد التخزين: {e}")
            raise
    
    def create_backup(self, description: str = "") -> Tuple[bool, str]:
        """
        إنشاء نسخة احتياطية جديدة ورفعها على Supabase
        
        Args:
            description: وصف النسخة الاحتياطية
            
        Returns:
            tuple: (نجح العملية, رسالة النتيجة)
        """
        # guard if Supabase disabled
        if self.supabase is None:
            return False, "backup functionality is disabled"
        try:
            # التحقق من وجود قاعدة البيانات
            if not config.DATABASE_PATH.exists():
                return False, "قاعدة البيانات غير موجودة"
            
            # إنشاء اسم الملف بالتاريخ والوقت
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}.zip"
            
            # إنشاء ملف مؤقت للنسخة الاحتياطية
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
                temp_path = temp_file.name
            
            try:
                # إنشاء أرشيف ZIP يحتوي على قاعدة البيانات
                with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                    # إضافة قاعدة البيانات
                    zip_file.write(config.DATABASE_PATH, "schools.db")
                    
                    # إضافة ملف معلومات النسخة الاحتياطية
                    backup_info = {
                        "created_at": datetime.now().isoformat(),
                        "description": description,
                        "database_size": os.path.getsize(config.DATABASE_PATH),
                        "version": config.APP_VERSION
                    }
                    
                    info_content = "\n".join([
                        f"تاريخ الإنشاء: {backup_info['created_at']}",
                        f"الوصف: {backup_info['description']}",
                        f"حجم قاعدة البيانات: {backup_info['database_size']} بايت",
                        f"إصدار التطبيق: {backup_info['version']}"
                    ])
                    
                    zip_file.writestr("backup_info.txt", info_content.encode('utf-8'))
                
                # رفع الملف على Supabase
                folder_path = f"backups/{datetime.now().strftime('%Y/%m')}"
                file_path = f"{folder_path}/{backup_filename}"
                
                with open(temp_path, 'rb') as file_data:
                    result = self.supabase.storage.from_(self.bucket_name).upload(
                        file_path,
                        file_data,
                        file_options={
                            "content-type": "application/zip",
                            "upsert": False
                        }
                    )
                
                # حفظ النسخة محلياً أيضاً
                local_backup_path = config.BACKUPS_DIR / "manual" / backup_filename
                shutil.copy2(temp_path, local_backup_path)
                
                self.logger.info(f"تم إنشاء النسخة الاحتياطية: {file_path}")
                return True, f"تم إنشاء النسخة الاحتياطية بنجاح\nالملف: {backup_filename}"
                
            finally:
                # حذف الملف المؤقت
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except StorageException as e:
            error_msg = f"خطأ في التخزين: {e}"
            self.logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            error_msg = f"خطأ في إنشاء النسخة الاحتياطية: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def list_backups(self) -> List[Dict]:
        """
        قائمة بجميع النسخ الاحتياطية المتاحة
        
        Returns:
            قائمة بالنسخ الاحتياطية مع معلوماتها
        """
        # guard if Supabase disabled
        if self.supabase is None:
            return []
        try:
            backups = []
            
            # جلب قائمة الملفات من Supabase
            result = self.supabase.storage.from_(self.bucket_name).list("backups", {
                "limit": 100,
                "sortBy": {"column": "created_at", "order": "desc"}
            })
            
            for item in result:
                if self._is_backup_folder(item):
                    # جلب الملفات من هذا المجلد
                    folder_files = self.supabase.storage.from_(self.bucket_name).list(
                        f"backups/{item['name']}", {"limit": 100}
                    )
                    
                    for folder_item in folder_files:
                        if self._is_backup_folder(folder_item):
                            # مجلد شهر، جلب الملفات منه
                            month_files = self.supabase.storage.from_(self.bucket_name).list(
                                f"backups/{item['name']}/{folder_item['name']}", {"limit": 100}
                            )
                            
                            for file_item in month_files:
                                if file_item['name'].endswith('.zip'):
                                    backup_info = self._parse_backup_info(
                                        f"backups/{item['name']}/{folder_item['name']}/{file_item['name']}",
                                        file_item
                                    )
                                    if backup_info:
                                        backups.append(backup_info)
            
            # ترتيب النسخ حسب التاريخ (الأحدث أولاً)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return backups
            
        except Exception as e:
            self.logger.error(f"خطأ في جلب قائمة النسخ الاحتياطية: {e}")
            return []
    
    def _is_backup_folder(self, item: Dict) -> bool:
        """التحقق من أن العنصر مجلد وليس ملف"""
        return item.get('id') is None and 'name' in item
    
    def _parse_backup_info(self, file_path: str, file_item: Dict) -> Optional[Dict]:
        """استخراج معلومات النسخة الاحتياطية"""
        try:
            filename = file_item['name']
            
            # استخراج التاريخ من اسم الملف
            if filename.startswith('backup_') and filename.endswith('.zip'):
                timestamp_str = filename[7:-4]  # إزالة 'backup_' و '.zip'
                
                try:
                    # تحويل timestamp إلى datetime
                    backup_date = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
                except ValueError:
                    backup_date = datetime.now()
                
                return {
                    'filename': filename,
                    'path': file_path,
                    'created_at': backup_date,
                    'size': file_item.get('metadata', {}).get('size', 0),
                    'formatted_date': backup_date.strftime("%Y-%m-%d %H:%M:%S"),
                    'formatted_size': self._format_file_size(
                        file_item.get('metadata', {}).get('size', 0)
                    )
                }
                
        except Exception as e:
            self.logger.error(f"خطأ في استخراج معلومات النسخة الاحتياطية: {e}")
            
        return None
    
    def _format_file_size(self, size_bytes: int) -> str:
        """تنسيق حجم الملف"""
        if size_bytes < 1024:
            return f"{size_bytes} بايت"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.1f} كيلوبايت"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} ميجابايت"
    
    def get_backup_url(self, file_path: str, expires_in: int = 3600) -> Optional[str]:
        """
        الحصول على رابط تحميل النسخة الاحتياطية
        
        Args:
            file_path: مسار الملف
            expires_in: مدة صلاحية الرابط بالثواني
            
        Returns:
            رابط التحميل أو None في حالة الخطأ
        """
        if self.supabase is None:
            return None
        try:
            result = self.supabase.storage.from_(self.bucket_name).create_signed_url(
                file_path, expires_in
            )
            return result.get('signedURL')
            
        except Exception as e:
            self.logger.error(f"خطأ في إنشاء رابط التحميل: {e}")
            return None
    
    def delete_backup(self, file_path: str) -> Tuple[bool, str]:
        """
        حذف نسخة احتياطية
        
        Args:
            file_path: مسار الملف
            
        Returns:
            tuple: (نجح العملية, رسالة النتيجة)
        """
        if self.supabase is None:
            return False, "backup functionality is disabled"
        try:
            result = self.supabase.storage.from_(self.bucket_name).remove([file_path])
            
            if result:
                self.logger.info(f"تم حذف النسخة الاحتياطية: {file_path}")
                return True, "تم حذف النسخة الاحتياطية بنجاح"
            else:
                return False, "فشل في حذف النسخة الاحتياطية"
                
        except Exception as e:
            error_msg = f"خطأ في حذف النسخة الاحتياطية: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def cleanup_old_backups(self, keep_days: int = 30) -> Tuple[bool, str]:
        """
        تنظيف النسخ الاحتياطية القديمة
        
        Args:
            keep_days: عدد الأيام للاحتفاظ بالنسخ
            
        Returns:
            tuple: (نجح العملية, رسالة النتيجة)
        """
        if self.supabase is None:
            return False, "backup functionality is disabled"
        try:
            backups = self.list_backups()
            cutoff_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - keep_days)
            
            deleted_count = 0
            for backup in backups:
                if backup['created_at'] < cutoff_date:
                    success, _ = self.delete_backup(backup['path'])
                    if success:
                        deleted_count += 1
            
            message = f"تم حذف {deleted_count} نسخة احتياطية قديمة"
            self.logger.info(message)
            return True, message
            
        except Exception as e:
            error_msg = f"خطأ في تنظيف النسخ الاحتياطية: {e}"
            self.logger.error(error_msg)
            return False, error_msg


# إنشاء مثيل مشترك من مدير النسخ الاحتياطية
backup_manager = BackupManager()
