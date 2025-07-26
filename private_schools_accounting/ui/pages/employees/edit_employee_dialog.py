#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة تعديل بيانات الموظف
"""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QPushButton, QComboBox, 
    QDoubleSpinBox, QTextEdit, QMessageBox,
    QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_database_operation


class EditEmployeeDialog(QDialog):
    """نافذة تعديل بيانات الموظف"""
    
    def __init__(self, employee_id, parent=None):
        super().__init__(parent)
        self.employee_id = employee_id
        self.setup_ui()
        self.setup_styles()
        self.load_schools()
        self.load_employee_data()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            self.setWindowTitle("تعديل بيانات الموظف")
            self.setModal(True)
            self.setFixedSize(450, 380)
            
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(20)
            
            # عنوان النافذة
            title_label = QLabel("تعديل بيانات الموظف")
            title_label.setObjectName("dialogTitle")
            layout.addWidget(title_label)
            
            # نموذج البيانات
            self.create_form(layout)
            
            # أزرار العمليات
            self.create_buttons(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد نافذة تعديل الموظف: {e}")
            raise
    
    def create_form(self, layout):
        """إنشاء نموذج البيانات"""
        try:
            form_frame = QFrame()
            form_frame.setObjectName("formFrame")
            
            form_layout = QFormLayout(form_frame)
            form_layout.setSpacing(15)
            form_layout.setContentsMargins(20, 20, 20, 20)
            
            # الاسم
            self.name_input = QLineEdit()
            self.name_input.setPlaceholderText("أدخل اسم الموظف")
            form_layout.addRow("الاسم *:", self.name_input)
            
            # المدرسة
            self.school_combo = QComboBox()
            self.school_combo.setMinimumWidth(200)
            form_layout.addRow("المدرسة *:", self.school_combo)
            
            # المهنة
            self.job_combo = QComboBox()
            self.job_combo.addItem("عامل", "عامل")
            self.job_combo.addItem("حارس", "حارس")
            self.job_combo.addItem("كاتب", "كاتب")
            self.job_combo.addItem("مخصص", "مخصص")
            form_layout.addRow("المهنة *:", self.job_combo)
            
            # الراتب الشهري
            self.salary_input = QDoubleSpinBox()
            self.salary_input.setRange(0, 999999)
            self.salary_input.setDecimals(2)
            self.salary_input.setSuffix(" ريال")
            form_layout.addRow("الراتب الشهري *:", self.salary_input)
            
            # رقم الهاتف
            self.phone_input = QLineEdit()
            self.phone_input.setPlaceholderText("05xxxxxxxx")
            form_layout.addRow("رقم الهاتف:", self.phone_input)
            
            # الملاحظات
            self.notes_input = QTextEdit()
            self.notes_input.setMaximumHeight(80)
            self.notes_input.setPlaceholderText("ملاحظات إضافية...")
            form_layout.addRow("ملاحظات:", self.notes_input)
            
            layout.addWidget(form_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء نموذج البيانات: {e}")
            raise
    
    def create_buttons(self, layout):
        """إنشاء أزرار العمليات"""
        try:
            buttons_frame = QFrame()
            buttons_layout = QHBoxLayout(buttons_frame)
            buttons_layout.setContentsMargins(0, 10, 0, 0)
            
            # زر الحفظ
            self.save_btn = QPushButton("حفظ التعديلات")
            self.save_btn.setObjectName("primaryButton")
            self.save_btn.setMinimumWidth(120)
            
            # زر الإلغاء
            self.cancel_btn = QPushButton("إلغاء")
            self.cancel_btn.setObjectName("secondaryButton")
            self.cancel_btn.setMinimumWidth(100)
            
            buttons_layout.addStretch()
            buttons_layout.addWidget(self.save_btn)
            buttons_layout.addWidget(self.cancel_btn)
            
            layout.addWidget(buttons_frame)
            
            # ربط الأحداث
            self.save_btn.clicked.connect(self.save_changes)
            self.cancel_btn.clicked.connect(self.reject)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الأزرار: {e}")
            raise
    
    def setup_styles(self):
        """إعداد أنماط العرض"""
        try:
            self.setStyleSheet("""
                QDialog {
                    background-color: #f8f9fa;
                }
                
                QLabel#dialogTitle {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2c3e50;
                    padding: 10px 0;
                    border-bottom: 2px solid #3498db;
                }
                
                QFrame#formFrame {
                    background-color: white;
                    border: 1px solid #dee2e6;
                    border-radius: 8px;
                }
                
                QLineEdit, QComboBox, QDoubleSpinBox, QTextEdit {
                    padding: 8px;
                    border: 1px solid #ced4da;
                    border-radius: 4px;
                    font-size: 12px;
                }
                
                QLineEdit:focus, QComboBox:focus, QDoubleSpinBox:focus, QTextEdit:focus {
                    border-color: #007bff;
                    outline: none;
                }
                
                QPushButton#primaryButton {
                    background-color: #007bff;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                
                QPushButton#primaryButton:hover {
                    background-color: #0056b3;
                }
                
                QPushButton#secondaryButton {
                    background-color: #6c757d;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                }
                
                QPushButton#secondaryButton:hover {
                    background-color: #545b62;
                }
            """)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الأنماط: {e}")
    
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute("SELECT id, name_ar FROM schools ORDER BY name_ar")
                schools = cursor.fetchall()
                
                self.school_combo.clear()
                for school in schools:
                    self.school_combo.addItem(school['name_ar'], school['id'])
                    
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المدارس:\n{e}")
    
    def load_employee_data(self):
        """تحميل بيانات الموظف"""
        try:
            with db_manager.get_cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM employees WHERE id = ?
                """, (self.employee_id,))
                
                employee = cursor.fetchone()
                if not employee:
                    QMessageBox.critical(self, "خطأ", "لم يتم العثور على بيانات الموظف")
                    self.reject()
                    return
                
                # ملء الحقول
                self.name_input.setText(employee['name'] or '')
                
                # تحديد المدرسة
                for i in range(self.school_combo.count()):
                    if self.school_combo.itemData(i) == employee['school_id']:
                        self.school_combo.setCurrentIndex(i)
                        break
                
                # تحديد المهنة
                for i in range(self.job_combo.count()):
                    if self.job_combo.itemData(i) == employee['job_type']:
                        self.job_combo.setCurrentIndex(i)
                        break
                
                self.salary_input.setValue(employee['monthly_salary'] or 0)
                self.phone_input.setText(employee['phone'] or '')
                self.notes_input.setPlainText(employee['notes'] or '')
                
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الموظف: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الموظف:\n{e}")
            self.reject()
    
    def validate_data(self):
        """التحقق من صحة البيانات"""
        try:
            # التحقق من الحقول المطلوبة
            if not self.name_input.text().strip():
                QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم الموظف")
                self.name_input.setFocus()
                return False
                
            if self.school_combo.currentData() is None:
                QMessageBox.warning(self, "خطأ", "يرجى اختيار المدرسة")
                self.school_combo.setFocus()
                return False
                
            if self.salary_input.value() <= 0:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال راتب شهري صحيح")
                self.salary_input.setFocus()
                return False
            
            # التحقق من رقم الهاتف إذا تم إدخاله
            phone = self.phone_input.text().strip()
            if phone and not phone.replace(' ', '').replace('-', '').isdigit():
                QMessageBox.warning(self, "خطأ", "رقم الهاتف غير صحيح")
                self.phone_input.setFocus()
                return False
                
            return True
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من البيانات: {e}")
            return False
    
    def save_changes(self):
        """حفظ التعديلات"""
        try:
            if not self.validate_data():
                return
                
            # جمع البيانات
            employee_data = {
                'name': self.name_input.text().strip(),
                'school_id': self.school_combo.currentData(),
                'job_type': self.job_combo.currentData(),
                'monthly_salary': self.salary_input.value(),
                'phone': self.phone_input.text().strip() or None,
                'notes': self.notes_input.toPlainText().strip() or None
            }
            
            # تحديث البيانات
            with db_manager.get_cursor() as cursor:
                cursor.execute("""
                    UPDATE employees 
                    SET name = ?, school_id = ?, job_type = ?, 
                        monthly_salary = ?, phone = ?, notes = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (
                    employee_data['name'],
                    employee_data['school_id'],
                    employee_data['job_type'],
                    employee_data['monthly_salary'],
                    employee_data['phone'],
                    employee_data['notes'],
                    self.employee_id
                ))
                
                log_database_operation("تعديل موظف", "employees", self.employee_id)
                
            QMessageBox.information(self, "نجح", "تم حفظ التعديلات بنجاح")
            self.accept()
            
        except Exception as e:
            logging.error(f"خطأ في حفظ التعديلات: {e}")
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ التعديلات:\n{e}")
