#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import os
from datetime import datetime

# إنشاء مجلد قاعدة البيانات إذا لم يكن موجوداً
db_dir = 'data/database'
os.makedirs(db_dir, exist_ok=True)

# إنشاء قاعدة البيانات
db_path = 'data/database/schools.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# إنشاء جدول المدارس
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

# إنشاء جدول الطلاب
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

# إنشاء جدول الأقساط
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

# إنشاء جدول الرسوم الإضافية
cursor.execute("""
    CREATE TABLE IF NOT EXISTS additional_fees (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        fee_type TEXT NOT NULL,
        amount DECIMAL(10,2) NOT NULL,
        paid BOOLEAN DEFAULT FALSE,
        payment_date DATE,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    )
""")

# إنشاء جدول المستخدمين
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL DEFAULT 'admin',
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# إنشاء جدول إعدادات التطبيق
cursor.execute("""
    CREATE TABLE IF NOT EXISTS app_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        setting_key TEXT UNIQUE NOT NULL,
        setting_value TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

# حفظ التغييرات
conn.commit()
conn.close()

print("تم إنشاء قاعدة البيانات بنجاح!")
