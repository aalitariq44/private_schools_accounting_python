#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إضافة راتب جديد
"""

import logging
from datetime import datetime, timedelta
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, QTextEdit,
    QDateEdit, QSpinBox, QDoubleSpinBox, QMessageBox,
    QFrame, QGroupBox, QCheckBox
)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator

from core.database.connection import db_manager
from core.utils.logger import log_user_action


class AddSalaryDialog(QDialog):
    """نافذة إضافة راتب جديد"""
    
    salary_added = pyqtSignal()  # إشارة إضافة راتب جديد
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.staff_list = []
        self.setup_ui()
        self.setup_connections()
        self.load_staff_data()
        self.calculate_default_period()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("إضافة راتب جديد")
        self.setFixedSize(500, 650)
        self.setModal(True)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # عنوان النافذة
        title_label = QLabel("إضافة راتب جديد")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addWidget(title_label)
        
        # مجموعة اختيار الموظف/المعلم
        staff_group = self.create_staff_group()
        main_layout.addWidget(staff_group)
        
        # مجموعة تفاصيل الراتب
        salary_group = self.create_salary_group()
        main_layout.addWidget(salary_group)
        
        # مجموعة فترة الراتب
        period_group = self.create_period_group()
        main_layout.addWidget(period_group)
        
        # مجموعة الملاحظات
        notes_group = self.create_notes_group()
        main_layout.addWidget(notes_group)
        
        # أزرار الحفظ والإلغاء
        buttons_layout = self.create_buttons()
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
        self.setup_styles()
        
    def create_staff_group(self):
        """إنشاء مجموعة اختيار الموظف/المعلم"""
        group = QGroupBox("بيانات الموظف/المعلم")
        layout = QFormLayout()
        
        # نوع الموظف
        self.staff_type_combo = QComboBox()
        self.staff_type_combo.addItem("معلم", "teacher")
        self.staff_type_combo.addItem("موظف", "employee")
        layout.addRow("نوع الموظف:", self.staff_type_combo)
        
        # قائمة الموظفين/المعلمين
        self.staff_combo = QComboBox()
        self.staff_combo.setMinimumWidth(300)
        layout.addRow("اختر الموظف/المعلم:", self.staff_combo)
        
        # عرض الراتب المسجل
        self.base_salary_label = QLabel("0.00 دينار")
        self.base_salary_label.setObjectName("salaryLabel")
        layout.addRow("الراتب المسجل:", self.base_salary_label)
        
        group.setLayout(layout)
        return group
    
    def create_salary_group(self):
        """إنشاء مجموعة تفاصيل الراتب"""
        group = QGroupBox("تفاصيل الراتب")
        layout = QFormLayout()
        
        # المبلغ المدفوع
        self.paid_amount_input = QDoubleSpinBox()
        self.paid_amount_input.setRange(0, 999999999)
        self.paid_amount_input.setDecimals(2)
        self.paid_amount_input.setSuffix(" دينار")
        self.paid_amount_input.setMinimumWidth(150)
        layout.addRow("المبلغ المدفوع:", self.paid_amount_input)
        
        # تاريخ الدفع
        self.payment_date_input = QDateEdit()
        self.payment_date_input.setDate(QDate.currentDate())
        self.payment_date_input.setCalendarPopup(True)
        self.payment_date_input.setMinimumWidth(150)
        layout.addRow("تاريخ الدفع:", self.payment_date_input)
        
        group.setLayout(layout)
        return group
    
    def create_period_group(self):
        """إنشاء مجموعة فترة الراتب"""
        group = QGroupBox("فترة الراتب")
        layout = QFormLayout()
        
        # من تاريخ
        self.from_date_input = QDateEdit()
        self.from_date_input.setCalendarPopup(True)
        self.from_date_input.setMinimumWidth(150)
        layout.addRow("من تاريخ:", self.from_date_input)
        
        # إلى تاريخ
        self.to_date_input = QDateEdit()
        self.to_date_input.setCalendarPopup(True)
        self.to_date_input.setMinimumWidth(150)
        layout.addRow("إلى تاريخ:", self.to_date_input)
        
        # عدد الأيام
        self.days_count_label = QLabel("30 يوم")
        self.days_count_label.setObjectName("daysLabel")
        layout.addRow("عدد الأيام:", self.days_count_label)
        
        group.setLayout(layout)
        return group
    
    def create_notes_group(self):
        """إنشاء مجموعة الملاحظات"""
        group = QGroupBox("ملاحظات")
        layout = QVBoxLayout()
        
        self.notes_input = QTextEdit()
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("أدخل أي ملاحظات إضافية...")
        layout.addWidget(self.notes_input)
        
        group.setLayout(layout)
        return group
    
    def create_buttons(self):
        """إنشاء أزرار الحفظ والإلغاء"""
        layout = QHBoxLayout()
        layout.addStretch()
        
        # زر الإلغاء
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancelButton")
        self.cancel_btn.setMinimumSize(100, 35)
        
        # زر الحفظ
        self.save_btn = QPushButton("إضافة الراتب")
        self.save_btn.setObjectName("saveButton")
        self.save_btn.setMinimumSize(120, 35)
        
        layout.addWidget(self.cancel_btn)
        layout.addWidget(self.save_btn)
        
        return layout
    
    def setup_connections(self):
        """إعداد الاتصالات والأحداث"""
        self.staff_type_combo.currentTextChanged.connect(self.load_staff_data)
        self.staff_combo.currentTextChanged.connect(self.update_base_salary)
        self.from_date_input.dateChanged.connect(self.calculate_days)
        self.to_date_input.dateChanged.connect(self.calculate_days)
        self.save_btn.clicked.connect(self.save_salary)
        self.cancel_btn.clicked.connect(self.reject)
    
    def setup_styles(self):
        """إعداد أنماط العرض"""
        self.setStyleSheet("""
            QDialog {
                background-color: #f8f9fa;
            }
            
            QLabel#titleLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 8px;
                margin-bottom: 10px;
            }
            
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #2c3e50;
            }
            
            QLabel#salaryLabel {
                color: #27ae60;
                font-weight: bold;
                font-size: 14px;
            }
            
            QLabel#daysLabel {
                color: #e74c3c;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton#saveButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            
            QPushButton#saveButton:hover {
                background-color: #2ecc71;
            }
            
            QPushButton#saveButton:pressed {
                background-color: #229954;
            }
            
            QPushButton#cancelButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
            }
            
            QPushButton#cancelButton:hover {
                background-color: #5a6268;
            }
            
            QComboBox, QDoubleSpinBox, QDateEdit, QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            
            QComboBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QTextEdit:focus {
                border-color: #007bff;
                outline: none;
            }
        """)
    
    def calculate_default_period(self):
        """حساب الفترة الافتراضية (30 يوم قبل اليوم الحالي)"""
        today = QDate.currentDate()
        thirty_days_ago = today.addDays(-30)
        
        self.from_date_input.setDate(thirty_days_ago)
        self.to_date_input.setDate(today)
        
        self.calculate_days()
    
    def calculate_days(self):
        """حساب عدد الأيام بين التاريخين"""
        from_date = self.from_date_input.date()
        to_date = self.to_date_input.date()
        
        if from_date <= to_date:
            days = from_date.daysTo(to_date) + 1  # +1 لتضمين اليوم الأخير
            self.days_count_label.setText(f"{days} يوم")
            self.days_count_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            self.days_count_label.setText("تاريخ غير صحيح!")
            self.days_count_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
    
    def load_staff_data(self):
        """تحميل بيانات الموظفين/المعلمين"""
        try:
            self.staff_combo.clear()
            self.staff_list = []
            
            staff_type = self.staff_type_combo.currentData()
            
            if staff_type == "teacher":
                table_name = "teachers"
                query = """
                    SELECT t.id, t.name, t.monthly_salary, s.name_ar as school_name
                    FROM teachers t
                    LEFT JOIN schools s ON t.school_id = s.id
                    ORDER BY t.name
                """
            else:  # employee
                table_name = "employees"
                query = """
                    SELECT e.id, e.name, e.monthly_salary, s.name_ar as school_name
                    FROM employees e
                    LEFT JOIN schools s ON e.school_id = s.id
                    ORDER BY e.name
                """
            
            with db_manager.get_cursor() as cursor:
                cursor.execute(query)
                staff_data = cursor.fetchall()
                
                for staff in staff_data:
                    display_text = f"{staff['name']} - {staff['school_name'] or 'غير محدد'}"
                    self.staff_combo.addItem(display_text)
                    self.staff_list.append({
                        'id': staff['id'],
                        'name': staff['name'],
                        'salary': staff['monthly_salary'] or 0,
                        'school': staff['school_name']
                    })
            
            # تحديث الراتب المعروض
            self.update_base_salary()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الموظفين: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الموظفين:\n{e}")
    
    def update_base_salary(self):
        """تحديث عرض الراتب المسجل"""
        try:
            current_index = self.staff_combo.currentIndex()
            if current_index >= 0 and current_index < len(self.staff_list):
                staff = self.staff_list[current_index]
                salary = staff['salary']
                self.base_salary_label.setText(f"{salary:.2f} دينار")
                
                # تعبئة المبلغ المدفوع بالراتب المسجل كقيمة افتراضية
                self.paid_amount_input.setValue(salary)
            else:
                self.base_salary_label.setText("0.00 دينار")
                self.paid_amount_input.setValue(0)
                
        except Exception as e:
            logging.error(f"خطأ في تحديث الراتب: {e}")
    
    def validate_inputs(self):
        """التحقق من صحة البيانات المدخلة"""
        # التحقق من اختيار موظف
        if self.staff_combo.currentIndex() < 0:
            QMessageBox.warning(self, "تحذير", "يرجى اختيار موظف أو معلم")
            return False
        
        # التحقق من المبلغ المدفوع
        if self.paid_amount_input.value() <= 0:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال مبلغ صحيح")
            return False
        
        # التحقق من صحة التواريخ
        from_date = self.from_date_input.date()
        to_date = self.to_date_input.date()
        
        if from_date > to_date:
            QMessageBox.warning(self, "تحذير", "تاريخ البداية يجب أن يكون قبل تاريخ النهاية")
            return False
        
        return True
    
    def save_salary(self):
        """حفظ الراتب الجديد"""
        try:
            if not self.validate_inputs():
                return
            
            # جمع البيانات
            staff_type = self.staff_type_combo.currentData()
            current_index = self.staff_combo.currentIndex()
            staff = self.staff_list[current_index]
            
            from_date = self.from_date_input.date().toPyDate()
            to_date = self.to_date_input.date().toPyDate()
            payment_date = self.payment_date_input.date().toPyDate()
            payment_time = datetime.now().time()
            
            days_count = (to_date - from_date).days + 1
            
            # إدخال البيانات في قاعدة البيانات
            with db_manager.get_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO salaries 
                    (staff_type, staff_id, staff_name, base_salary, paid_amount, 
                     from_date, to_date, days_count, payment_date, payment_time, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    staff_type,
                    staff['id'],
                    staff['name'],
                    staff['salary'],
                    self.paid_amount_input.value(),
                    from_date,
                    to_date,
                    days_count,
                    payment_date,
                    payment_time,
                    self.notes_input.toPlainText().strip() or None
                ))
            
            # تسجيل العملية
            log_user_action(
                f"إضافة راتب {staff_type}",
                f"الاسم: {staff['name']}, المبلغ: {self.paid_amount_input.value()}"
            )
            
            # إرسال إشارة التحديث
            self.salary_added.emit()
            
            QMessageBox.information(self, "نجح", "تم إضافة الراتب بنجاح")
            self.accept()
            
        except Exception as e:
            logging.error(f"خطأ في حفظ الراتب: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ الراتب:\n{e}")
