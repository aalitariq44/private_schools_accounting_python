#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إدارة اتصال قاعدة البيانات وإنشاء الجداول
"""

import sqlite3
import logging
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, List, Dict, Any

import config


class DatabaseManager:
    """مدير قاعدة البيانات"""
    
    def __init__(self):
        """تهيئة مدير قاعدة البيانات"""
        self.db_path = config.DATABASE_PATH
        self.connection = None
        
    def get_connection(self) -> sqlite3.Connection:
        """الحصول على اتصال قاعدة البيانات"""
        try:
            if self.connection is None:
                self.connection = sqlite3.connect(
                    str(self.db_path),
                    check_same_thread=False
                )
                self.connection.row_factory = sqlite3.Row
                # تفعيل المفاتيح الأجنبية
                self.connection.execute("PRAGMA foreign_keys = ON")
                
            return self.connection
            
        except Exception as e:
            logging.error(f"خطأ في الاتصال بقاعدة البيانات: {e}")
            raise
    
    @contextmanager
    def get_cursor(self):
        """الحصول على cursor مع إدارة تلقائية للموارد"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception as e:
            conn.rollback()
            logging.error(f"خطأ في قاعدة البيانات: {e}")
            raise
        finally:
            cursor.close()
    
    def close_connection(self):
        """إغلاق اتصال قاعدة البيانات"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def initialize_database(self) -> bool:
        """تهيئة قاعدة البيانات وإنشاء الجداول"""
        try:
            # التأكد من وجود مجلد قاعدة البيانات
            config.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
            
            # إنشاء الجداول
            self.create_tables()
            
            logging.info("تم تهيئة قاعدة البيانات بنجاح")
            return True
            
        except Exception as e:
            logging.error(f"خطأ في تهيئة قاعدة البيانات: {e}")
            return False
    
    def create_tables(self):
        """إنشاء جداول قاعدة البيانات"""
        try:
            with self.get_cursor() as cursor:
                # جدول المستخدمين (للمصادقة)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL DEFAULT 'admin',
                        password_hash TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # جدول المدارس
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS schools (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name_ar TEXT NOT NULL,
                        name_en TEXT,
                        logo_path TEXT,
                        address TEXT,
                        phone TEXT,
                        principal_name TEXT,
                        school_types TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # جدول الطلاب
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS students (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        national_id_number TEXT,
                        school_id INTEGER NOT NULL,
                        grade TEXT NOT NULL,
                        section TEXT NOT NULL,
                        academic_year TEXT,
                        gender TEXT NOT NULL,
                        phone TEXT,
                        guardian_name TEXT,
                        guardian_phone TEXT,
                        total_fee DECIMAL(10,2) NOT NULL,
                        start_date DATE NOT NULL,
                        status TEXT DEFAULT 'نشط',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (school_id) REFERENCES schools(id) ON DELETE CASCADE
                    )
                """)
                
                # جدول الأقساط
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS installments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER NOT NULL,
                        type TEXT DEFAULT 'قسط دراسي',
                        amount DECIMAL(10,2) NOT NULL,
                        due_date DATE,
                        payment_date DATE NOT NULL,
                        payment_time TIME NOT NULL,
                        paid_amount DECIMAL(10,2) DEFAULT 0,
                        status TEXT DEFAULT 'غير مدفوع',
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                    )
                """)
                
                # جدول الرسوم الإضافية
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS additional_fees (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER NOT NULL,
                        fee_type TEXT NOT NULL,
                        amount DECIMAL(10,2) NOT NULL,
                        due_date DATE,
                        paid BOOLEAN DEFAULT FALSE,
                        payment_date DATE,
                        collection_date DATE,
                        collected_amount DECIMAL(10,2) DEFAULT 0,
                        status TEXT DEFAULT 'غير محصل',
                        notes TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
                    )
                """)
                
                # جدول إعدادات التطبيق
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS app_settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        setting_key TEXT UNIQUE NOT NULL,
                        setting_value TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # إنشاء الفهارس لتحسين الأداء
                self.create_indexes(cursor)
                
                logging.info("تم إنشاء جداول قاعدة البيانات بنجاح")
                
        except Exception as e:
            logging.error(f"خطأ في إنشاء جداول قاعدة البيانات: {e}")
            raise
    
    def create_indexes(self, cursor):
        """إنشاء فهارس قاعدة البيانات"""
        try:
            # فهارس الطلاب
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_school_id ON students(school_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_name ON students(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_students_grade ON students(grade)")
            
            # فهارس الأقساط
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_installments_student_id ON installments(student_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_installments_payment_date ON installments(payment_date)")
            
            # فهارس الرسوم الإضافية
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_additional_fees_student_id ON additional_fees(student_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_additional_fees_paid ON additional_fees(paid)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_additional_fees_due_date ON additional_fees(due_date)")
            
            logging.info("تم إنشاء فهارس قاعدة البيانات بنجاح")
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء فهارس قاعدة البيانات: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """تنفيذ استعلام SELECT وإرجاع النتائج"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.fetchall()
                
        except Exception as e:
            logging.error(f"خطأ في تنفيذ الاستعلام: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """تنفيذ استعلام INSERT/UPDATE/DELETE وإرجاع عدد الصفوف المتأثرة"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.rowcount
                
        except Exception as e:
            logging.error(f"خطأ في تنفيذ التحديث: {e}")
            raise
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """تنفيذ استعلام INSERT وإرجاع ID السجل الجديد"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(query, params)
                return cursor.lastrowid
                
        except Exception as e:
            logging.error(f"خطأ في تنفيذ الإدخال: {e}")
            raise
    
    def get_table_info(self, table_name: str) -> List[Dict[str, Any]]:
        """الحصول على معلومات جدول"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = cursor.fetchall()
                return [dict(column) for column in columns]
                
        except Exception as e:
            logging.error(f"خطأ في الحصول على معلومات الجدول {table_name}: {e}")
            raise
    
    def backup_database(self, backup_path: str) -> bool:
        """إنشاء نسخة احتياطية من قاعدة البيانات"""
        try:
            import shutil
            shutil.copy2(str(self.db_path), backup_path)
            logging.info(f"تم إنشاء نسخة احتياطية في: {backup_path}")
            return True
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء النسخة الاحتياطية: {e}")
            return False
    
    def restore_database(self, backup_path: str) -> bool:
        """استعادة قاعدة البيانات من نسخة احتياطية"""
        try:
            import shutil
            # إغلاق الاتصال الحالي
            self.close_connection()
            
            # استعادة النسخة الاحتياطية
            shutil.copy2(backup_path, str(self.db_path))
            
            logging.info(f"تم استعادة قاعدة البيانات من: {backup_path}")
            return True
            
        except Exception as e:
            logging.error(f"خطأ في استعادة قاعدة البيانات: {e}")
            return False
    
    def __del__(self):
        """مدمر الفئة - إغلاق الاتصال"""
        self.close_connection()


# إنشاء مثيل مشترك من مدير قاعدة البيانات
db_manager = DatabaseManager()
