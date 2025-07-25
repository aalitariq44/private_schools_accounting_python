#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إضافة رسم إضافي جديد
"""

import logging
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QPushButton, QLineEdit, QDateEdit, QTextEdit, QComboBox,
    QMessageBox, QFrame, QDoubleSpinBox, QCheckBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation


class AddAdditionalFeeDialog(QDialog):
    """نافذة إضافة رسم إضافي جديد"""
    
    def __init__(self, student_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.setup_defaults()
        
        log_user_action(f"فتح نافذة إضافة رسم إضافي للطالب: {student_id}")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            self.setWindowTitle("إضافة رسم إضافي")
            self.setModal(True)
            self.setFixedSize(450, 400)
            
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            # العنوان
            title_label = QLabel("إضافة رسم إضافي جديد")
            title_label.setObjectName("dialogTitle")
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
            
            # نموذج الإدخال
            form_layout = QFormLayout()
            form_layout.setSpacing(12)
            
            # نوع الرسم
            self.fee_type_combo = QComboBox()
            self.fee_type_combo.setObjectName("feeTypeCombo")
            self.fee_type_combo.addItems([
                "رسوم التسجيل",
                "الزي المدرسي",
                "الكتب",
                "القرطاسية",
                "رسوم النقل",
                "رسوم الأنشطة",
                "رسوم الامتحانات",
                "رسم مخصص"
            ])
            form_layout.addRow("نوع الرسم:", self.fee_type_combo)
            
            # رسم مخصص
            self.custom_fee_input = QLineEdit()
            self.custom_fee_input.setObjectName("customFeeInput")
            self.custom_fee_input.setPlaceholderText("أدخل نوع الرسم المخصص...")
            self.custom_fee_input.setVisible(False)
            form_layout.addRow("النوع المخصص:", self.custom_fee_input)
            
            # مبلغ الرسم
            self.amount_input = QDoubleSpinBox()
            self.amount_input.setObjectName("amountInput")
            self.amount_input.setMinimum(1.0)
            self.amount_input.setMaximum(9999999.0)
            self.amount_input.setDecimals(0)
            self.amount_input.setSuffix(" د.ع")
            self.amount_input.setValue(50000.0)
            form_layout.addRow("مبلغ الرسم:", self.amount_input)
            
            # تاريخ الاستحقاق
            self.due_date = QDateEdit()
            self.due_date.setObjectName("dateInput")
            self.due_date.setCalendarPopup(True)
            self.due_date.setDisplayFormat("yyyy-MM-dd")
            form_layout.addRow("تاريخ الاستحقاق:", self.due_date)
            
            # حالة الدفع
            self.paid_checkbox = QCheckBox("تم الدفع")
            self.paid_checkbox.setObjectName("paidCheckbox")
            form_layout.addRow("حالة الدفع:", self.paid_checkbox)
            
            # تاريخ الدفع
            self.payment_date = QDateEdit()
            self.payment_date.setObjectName("dateInput")
            self.payment_date.setCalendarPopup(True)
            self.payment_date.setDisplayFormat("yyyy-MM-dd")
            self.payment_date.setEnabled(False)
            form_layout.addRow("تاريخ الدفع:", self.payment_date)
            
            # الملاحظات
            self.notes_input = QTextEdit()
            self.notes_input.setObjectName("notesInput")
            self.notes_input.setMaximumHeight(80)
            self.notes_input.setPlaceholderText("أدخل أي ملاحظات إضافية...")
            form_layout.addRow("الملاحظات:", self.notes_input)
            
            layout.addLayout(form_layout)
            
            # أزرار العمليات
            buttons_layout = QHBoxLayout()
            
            self.save_button = QPushButton("حفظ الرسم")
            self.save_button.setObjectName("saveButton")
            buttons_layout.addWidget(self.save_button)
            
            self.cancel_button = QPushButton("إلغاء")
            self.cancel_button.setObjectName("cancelButton")
            buttons_layout.addWidget(self.cancel_button)
            
            layout.addLayout(buttons_layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة نافذة إضافة الرسم الإضافي: {e}")
            raise
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            self.save_button.clicked.connect(self.save_additional_fee)
            self.cancel_button.clicked.connect(self.reject)
            
            # إظهار/إخفاء حقل الرسم المخصص
            self.fee_type_combo.currentTextChanged.connect(self.on_fee_type_changed)
            
            # تفعيل/تعطيل تاريخ الدفع
            self.paid_checkbox.toggled.connect(self.on_paid_toggled)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def setup_defaults(self):
        """إعداد القيم الافتراضية"""
        try:
            # تعيين تاريخ الاستحقاق (شهر من الآن)
            current_date = QDate.currentDate()
            due_date = current_date.addDays(30)
            self.due_date.setDate(due_date)
            
            # تعيين تاريخ الدفع الحالي
            self.payment_date.setDate(current_date)
            
            # تركيز على نوع الرسم
            self.fee_type_combo.setFocus()
            
        except Exception as e:
            logging.error(f"خطأ في إعداد القيم الافتراضية: {e}")
    
    def on_fee_type_changed(self, fee_type):
        """معالج تغيير نوع الرسم"""
        try:
            if fee_type == "رسم مخصص":
                self.custom_fee_input.setVisible(True)
                self.custom_fee_input.setFocus()
            else:
                self.custom_fee_input.setVisible(False)
                self.custom_fee_input.clear()
            
        except Exception as e:
            logging.error(f"خطأ في معالج تغيير نوع الرسم: {e}")
    
    def on_paid_toggled(self, checked):
        """معالج تغيير حالة الدفع"""
        try:
            self.payment_date.setEnabled(checked)
            if checked:
                # تعيين تاريخ الدفع الحالي
                self.payment_date.setDate(QDate.currentDate())
            
        except Exception as e:
            logging.error(f"خطأ في معالج تغيير حالة الدفع: {e}")
    
    def validate_input(self):
        """التحقق من صحة البيانات المدخلة"""
        try:
            # التحقق من نوع الرسم
            fee_type = self.fee_type_combo.currentText()
            if fee_type == "رسم مخصص":
                custom_fee = self.custom_fee_input.text().strip()
                if not custom_fee:
                    QMessageBox.warning(self, "خطأ", "يجب إدخال نوع الرسم المخصص")
                    self.custom_fee_input.setFocus()
                    return False
            
            # التحقق من المبلغ
            amount = self.amount_input.value()
            if amount <= 0:
                QMessageBox.warning(self, "خطأ", "يجب إدخال مبلغ صحيح")
                self.amount_input.setFocus()
                return False
            
            # التحقق من تاريخ الاستحقاق
            due_date = self.due_date.date().toPyDate()
            if due_date < date.today():
                reply = QMessageBox.question(
                    self, "تأكيد",
                    "تاريخ الاستحقاق في الماضي. هل تريد المتابعة؟",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    self.due_date.setFocus()
                    return False
            
            # التحقق من تاريخ الدفع إذا كان مدفوعاً
            if self.paid_checkbox.isChecked():
                payment_date = self.payment_date.date().toPyDate()
                if payment_date > date.today():
                    reply = QMessageBox.question(
                        self, "تأكيد",
                        "تاريخ الدفع في المستقبل. هل تريد المتابعة؟",
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )
                    if reply == QMessageBox.No:
                        self.payment_date.setFocus()
                        return False
            
            return True
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من البيانات: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في التحقق من البيانات: {str(e)}")
            return False
    
    def save_additional_fee(self):
        """حفظ الرسم الإضافي الجديد"""
        try:
            if not self.validate_input():
                return
            
            # جمع البيانات
            fee_type = self.fee_type_combo.currentText()
            if fee_type == "رسم مخصص":
                fee_type = self.custom_fee_input.text().strip()
            
            amount = self.amount_input.value()
            due_date = self.due_date.date().toString("yyyy-MM-dd")
            paid = self.paid_checkbox.isChecked()
            payment_date = self.payment_date.date().toString("yyyy-MM-dd") if paid else None
            notes = self.notes_input.toPlainText().strip()
            
            # تحديد الحالة
            status = 'محصل' if paid else 'غير محصل'
            
            # إدراج الرسم في قاعدة البيانات مع الحقول الصحيحة
            query = """
                INSERT INTO additional_fees 
                (student_id, fee_type, amount, due_date, paid, payment_date, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                self.student_id, fee_type, amount, due_date, 
                paid, payment_date, status, notes if notes else None
            )
            
            result = db_manager.execute_query(query, params)
            
            if result is not None:
                # تسجيل العملية
                log_database_operation(
                    f"إضافة رسم إضافي جديد - الطالب: {self.student_id}, "
                    f"النوع: {fee_type}, المبلغ: {amount}"
                )
                log_user_action(
                    f"إضافة رسم إضافي ({fee_type}) بمبلغ {amount:,.0f} د.ع للطالب: {self.student_id}"
                )
                
                QMessageBox.information(self, "نجح", "تم حفظ الرسم الإضافي بنجاح")
                self.accept()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في حفظ الرسم الإضافي")
            
        except Exception as e:
            logging.error(f"خطأ في حفظ الرسم الإضافي: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في حفظ الرسم الإضافي: {str(e)}")
    
    def setup_styles(self):
        """إعداد التنسيقات"""
        try:
            style = """
                /* النافذة الرئيسية */
                QDialog {
                    background-color: #F8F9FA;
                    font-family: 'Segoe UI', Tahoma, Arial;
                    font-size: 14px;
                }
                
                /* العنوان */
                #dialogTitle {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    padding: 10px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #8E44AD, stop:1 #9B59B6);
                    color: white;
                    border-radius: 8px;
                    margin-bottom: 10px;
                }
                
                /* حقول الإدخال */
                #feeTypeCombo {
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                    background-color: white;
                }
                
                #feeTypeCombo:focus {
                    border-color: #8E44AD;
                    background-color: #F4F0F8;
                }
                
                #customFeeInput {
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                    background-color: white;
                }
                
                #customFeeInput:focus {
                    border-color: #8E44AD;
                    background-color: #F4F0F8;
                }
                
                #amountInput {
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                    background-color: white;
                }
                
                #amountInput:focus {
                    border-color: #8E44AD;
                    background-color: #F4F0F8;
                }
                
                #dateInput {
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                    background-color: white;
                }
                
                #dateInput:focus {
                    border-color: #8E44AD;
                    background-color: #F4F0F8;
                }
                
                #dateInput:disabled {
                    background-color: #F0F0F0;
                    color: #888888;
                }
                
                #notesInput {
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                    background-color: white;
                }
                
                #notesInput:focus {
                    border-color: #8E44AD;
                    background-color: #F4F0F8;
                }
                
                /* صندوق الاختيار */
                #paidCheckbox {
                    font-size: 14px;
                    font-weight: bold;
                    color: #27AE60;
                }
                
                #paidCheckbox::indicator {
                    width: 18px;
                    height: 18px;
                }
                
                #paidCheckbox::indicator:unchecked {
                    border: 2px solid #BDC3C7;
                    border-radius: 4px;
                    background-color: white;
                }
                
                #paidCheckbox::indicator:checked {
                    border: 2px solid #27AE60;
                    border-radius: 4px;
                    background-color: #27AE60;
                    image: url(:/icons/check.png);
                }
                
                /* التسميات */
                QLabel {
                    color: #2C3E50;
                    font-weight: bold;
                    font-size: 14px;
                }
                
                /* الأزرار */
                #saveButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #8E44AD, stop:1 #9B59B6);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                
                #saveButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #9B59B6, stop:1 #A569BD);
                }
                
                #saveButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #7D3C98, stop:1 #884EA0);
                }
                
                #cancelButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #95A5A6, stop:1 #7F8C8D);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                
                #cancelButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #7F8C8D, stop:1 #566769);
                }
                
                #cancelButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #566769, stop:1 #2C3E50);
                }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التنسيقات: {e}")
