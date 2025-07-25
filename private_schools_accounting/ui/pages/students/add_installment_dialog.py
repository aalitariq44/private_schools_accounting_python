#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إضافة قسط جديد
"""

import logging
from datetime import datetime, date, time
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QPushButton, QLineEdit, QDateEdit, QTimeEdit, QTextEdit,
    QMessageBox, QFrame, QSpinBox, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont, QDoubleValidator

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation


class AddInstallmentDialog(QDialog):
    """نافذة إضافة قسط جديد"""
    
    def __init__(self, student_id, max_amount, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.max_amount = max_amount
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.setup_defaults()
        
        log_user_action(f"فتح نافذة إضافة قسط للطالب: {student_id}")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            self.setWindowTitle("إضافة قسط جديد")
            self.setModal(True)
            self.setFixedSize(400, 350)
            
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            # العنوان
            title_label = QLabel("إضافة قسط جديد")
            title_label.setObjectName("dialogTitle")
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
            
            # معلومات المبلغ المتبقي
            info_frame = QFrame()
            info_frame.setObjectName("infoFrame")
            info_layout = QHBoxLayout(info_frame)
            
            info_label = QLabel(f"المبلغ المتبقي: {self.max_amount:,.0f} د.ع")
            info_label.setObjectName("infoLabel")
            info_label.setAlignment(Qt.AlignCenter)
            info_layout.addWidget(info_label)
            
            layout.addWidget(info_frame)
            
            # نموذج الإدخال
            form_layout = QFormLayout()
            form_layout.setSpacing(12)
            
            # مبلغ القسط
            self.amount_input = QDoubleSpinBox()
            self.amount_input.setObjectName("amountInput")
            self.amount_input.setMinimum(1.0)
            self.amount_input.setMaximum(self.max_amount)
            self.amount_input.setDecimals(0)
            self.amount_input.setSuffix(" د.ع")
            self.amount_input.setValue(self.max_amount)
            form_layout.addRow("مبلغ القسط:", self.amount_input)
            
            # تاريخ الدفعة
            self.payment_date = QDateEdit()
            self.payment_date.setObjectName("dateInput")
            self.payment_date.setCalendarPopup(True)
            self.payment_date.setDisplayFormat("yyyy-MM-dd")
            form_layout.addRow("تاريخ الدفعة:", self.payment_date)
            
            # وقت الدفعة
            self.payment_time = QTimeEdit()
            self.payment_time.setObjectName("timeInput")
            self.payment_time.setDisplayFormat("HH:mm:ss")
            form_layout.addRow("وقت الدفعة:", self.payment_time)
            
            # الملاحظات
            self.notes_input = QTextEdit()
            self.notes_input.setObjectName("notesInput")
            self.notes_input.setMaximumHeight(80)
            self.notes_input.setPlaceholderText("أدخل أي ملاحظات إضافية...")
            form_layout.addRow("الملاحظات:", self.notes_input)
            
            layout.addLayout(form_layout)
            
            # أزرار العمليات
            buttons_layout = QHBoxLayout()
            
            self.save_button = QPushButton("حفظ القسط")
            self.save_button.setObjectName("saveButton")
            buttons_layout.addWidget(self.save_button)
            
            self.cancel_button = QPushButton("إلغاء")
            self.cancel_button.setObjectName("cancelButton")
            buttons_layout.addWidget(self.cancel_button)
            
            layout.addLayout(buttons_layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة نافذة إضافة القسط: {e}")
            raise
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            self.save_button.clicked.connect(self.save_installment)
            self.cancel_button.clicked.connect(self.reject)
            
            # التحقق من صحة المبلغ عند التغيير
            self.amount_input.valueChanged.connect(self.validate_amount)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def setup_defaults(self):
        """إعداد القيم الافتراضية"""
        try:
            # تعيين التاريخ والوقت الحاليين
            current_date = QDate.currentDate()
            current_time = QTime.currentTime()
            
            self.payment_date.setDate(current_date)
            self.payment_time.setTime(current_time)
            
            # تركيز على حقل المبلغ
            self.amount_input.setFocus()
            self.amount_input.selectAll()
            
        except Exception as e:
            logging.error(f"خطأ في إعداد القيم الافتراضية: {e}")
    
    def validate_amount(self):
        """التحقق من صحة المبلغ"""
        try:
            amount = self.amount_input.value()
            
            if amount > self.max_amount:
                self.amount_input.setValue(self.max_amount)
                QMessageBox.warning(
                    self, "تحذير", 
                    f"لا يمكن أن يكون المبلغ أكبر من المتبقي ({self.max_amount:,.0f} د.ع)"
                )
            elif amount <= 0:
                self.amount_input.setValue(1)
                QMessageBox.warning(self, "تحذير", "يجب أن يكون المبلغ أكبر من صفر")
            
        except Exception as e:
            logging.error(f"خطأ في التحقق من المبلغ: {e}")
    
    def validate_input(self):
        """التحقق من صحة البيانات المدخلة"""
        try:
            # التحقق من المبلغ
            amount = self.amount_input.value()
            if amount <= 0:
                QMessageBox.warning(self, "خطأ", "يجب إدخال مبلغ صحيح")
                self.amount_input.setFocus()
                return False
            
            if amount > self.max_amount:
                QMessageBox.warning(
                    self, "خطأ", 
                    f"لا يمكن أن يكون المبلغ أكبر من المتبقي ({self.max_amount:,.0f} د.ع)"
                )
                self.amount_input.setFocus()
                return False
            
            # التحقق من التاريخ
            payment_date = self.payment_date.date().toPyDate()
            if payment_date > date.today():
                reply = QMessageBox.question(
                    self, "تأكيد",
                    "التاريخ المحدد في المستقبل. هل تريد المتابعة؟",
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
    
    def save_installment(self):
        """حفظ القسط الجديد"""
        try:
            if not self.validate_input():
                return
            
            # جمع البيانات
            amount = self.amount_input.value()
            payment_date = self.payment_date.date().toString("yyyy-MM-dd")
            payment_time = self.payment_time.time().toString("HH:mm:ss")
            notes = self.notes_input.toPlainText().strip()
            
            # إدراج القسط في قاعدة البيانات مع البنية الجديدة
            query = """
                INSERT INTO installments (student_id, amount, payment_date, payment_time, paid_amount, status, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """
            params = (
                self.student_id, 
                amount, 
                payment_date, 
                payment_time, 
                amount,  # المبلغ المدفوع = المبلغ الكامل
                'مدفوع',  # الحالة
                notes if notes else None
            )
            
            result = db_manager.execute_query(query, params)
            
            if result is not None:
                # تسجيل العملية
                log_database_operation(
                    f"إضافة قسط جديد - الطالب: {self.student_id}, "
                    f"المبلغ: {amount}, التاريخ: {payment_date}"
                )
                log_user_action(f"إضافة قسط بمبلغ {amount:,.0f} د.ع للطالب: {self.student_id}")
                
                QMessageBox.information(self, "نجح", "تم حفظ القسط بنجاح")
                self.accept()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في حفظ القسط")
            
        except Exception as e:
            logging.error(f"خطأ في حفظ القسط: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في حفظ القسط: {str(e)}")
    
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
                        stop:0 #3498DB, stop:1 #2980B9);
                    color: white;
                    border-radius: 8px;
                    margin-bottom: 10px;
                }
                
                /* إطار المعلومات */
                #infoFrame {
                    background-color: #E8F5E8;
                    border: 2px solid #27AE60;
                    border-radius: 8px;
                    padding: 8px;
                }
                
                #infoLabel {
                    font-size: 16px;
                    font-weight: bold;
                    color: #27AE60;
                }
                
                /* حقول الإدخال */
                #amountInput {
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                    background-color: white;
                }
                
                #amountInput:focus {
                    border-color: #3498DB;
                    background-color: #F0F8FF;
                }
                
                #dateInput, #timeInput {
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                    background-color: white;
                }
                
                #dateInput:focus, #timeInput:focus {
                    border-color: #3498DB;
                    background-color: #F0F8FF;
                }
                
                #notesInput {
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    padding: 8px;
                    font-size: 14px;
                    background-color: white;
                }
                
                #notesInput:focus {
                    border-color: #3498DB;
                    background-color: #F0F8FF;
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
                        stop:0 #27AE60, stop:1 #229954);
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                
                #saveButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #229954, stop:1 #1E8449);
                }
                
                #saveButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #1E8449, stop:1 #186A3B);
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
