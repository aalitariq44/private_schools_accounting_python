#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة تسجيل الدخول
"""

import logging
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QFrame, QMessageBox, QCheckBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon, QKeySequence

import config
from core.auth.login_manager import auth_manager
from core.utils.logger import auth_logger


class LoginWindow(QDialog):
    """نافذة تسجيل الدخول"""
    
    # إشارة تسجيل دخول ناجح
    login_successful = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.login_attempts = 0
        self.max_attempts = 3
        self.setup_ui()
        self.setup_styles()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # إعداد النافذة
            self.setWindowTitle("تسجيل الدخول - حسابات المدارس الأهلية")
            self.setFixedSize(400, 300)
            self.setModal(True)
            self.setLayoutDirection(Qt.RightToLeft)
            
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            main_layout.setSpacing(20)
            main_layout.setContentsMargins(30, 30, 30, 30)
            
            # رأس النافذة
            self.create_header(main_layout)
            
            # نموذج تسجيل الدخول
            self.create_login_form(main_layout)
            
            # الأزرار
            self.create_buttons(main_layout)
            
            self.setLayout(main_layout)
            
            # تركيز على حقل كلمة المرور
            QTimer.singleShot(100, self.password_input.setFocus)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة تسجيل الدخول: {e}")
            raise
    
    def create_header(self, layout):
        """إنشاء رأس النافذة"""
        try:
            # إطار الرأس
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            header_layout = QVBoxLayout(header_frame)
            header_layout.setAlignment(Qt.AlignCenter)
            
            # أيقونة التطبيق
            icon_label = QLabel()
            icon_label.setAlignment(Qt.AlignCenter)
            icon_label.setFixedSize(60, 60)
            icon_label.setStyleSheet("""
                QLabel {
                    background-color: #2C3E50;
                    border-radius: 30px;
                    border: 2px solid #3498DB;
                }
            """)
            header_layout.addWidget(icon_label)
            
            # عنوان التطبيق
            title_label = QLabel("تسجيل الدخول")
            title_label.setObjectName("titleLabel")
            title_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(title_label)
            
            # نص توضيحي
            subtitle_label = QLabel("حسابات المدارس الأهلية")
            subtitle_label.setObjectName("subtitleLabel")
            subtitle_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(subtitle_label)
            
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس النافذة: {e}")
            raise
    
    def create_login_form(self, layout):
        """إنشاء نموذج تسجيل الدخول"""
        try:
            # إطار النموذج
            form_frame = QFrame()
            form_frame.setObjectName("formFrame")
            form_layout = QVBoxLayout(form_frame)
            form_layout.setSpacing(15)
            
            # اسم المستخدم (مخفي لأن هناك مستخدم واحد فقط)
            self.username_input = QLineEdit()
            self.username_input.setText("admin")  # المستخدم الافتراضي
            self.username_input.setVisible(False)  # مخفي
            
            # تسمية كلمة المرور
            password_label = QLabel("كلمة المرور:")
            password_label.setObjectName("fieldLabel")
            form_layout.addWidget(password_label)
            
            # حقل كلمة المرور
            self.password_input = QLineEdit()
            self.password_input.setObjectName("passwordInput")
            self.password_input.setEchoMode(QLineEdit.Password)
            self.password_input.setPlaceholderText("أدخل كلمة المرور...")
            self.password_input.returnPressed.connect(self.login)
            form_layout.addWidget(self.password_input)
            
            # خيار إظهار كلمة المرور
            self.show_password_checkbox = QCheckBox("إظهار كلمة المرور")
            self.show_password_checkbox.setObjectName("showPasswordCheckbox")
            self.show_password_checkbox.toggled.connect(self.toggle_password_visibility)
            form_layout.addWidget(self.show_password_checkbox)
            
            # رسالة الخطأ
            self.error_label = QLabel()
            self.error_label.setObjectName("errorLabel")
            self.error_label.setAlignment(Qt.AlignCenter)
            self.error_label.setWordWrap(True)
            self.error_label.hide()
            form_layout.addWidget(self.error_label)
            
            layout.addWidget(form_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء نموذج تسجيل الدخول: {e}")
            raise
    
    def create_buttons(self, layout):
        """إنشاء الأزرار"""
        try:
            # إطار الأزرار
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(15)
            
            # زر الإلغاء
            self.cancel_button = QPushButton("إلغاء")
            self.cancel_button.setObjectName("cancelButton")
            self.cancel_button.clicked.connect(self.reject)
            buttons_layout.addWidget(self.cancel_button)
            
            # زر تسجيل الدخول
            self.login_button = QPushButton("تسجيل الدخول")
            self.login_button.setObjectName("loginButton")
            self.login_button.clicked.connect(self.login)
            self.login_button.setDefault(True)
            buttons_layout.addWidget(self.login_button)
            
            layout.addLayout(buttons_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الأزرار: {e}")
            raise
    
    def toggle_password_visibility(self, checked):
        """تبديل إظهار/إخفاء كلمة المرور"""
        try:
            if checked:
                self.password_input.setEchoMode(QLineEdit.Normal)
            else:
                self.password_input.setEchoMode(QLineEdit.Password)
                
        except Exception as e:
            logging.error(f"خطأ في تبديل إظهار كلمة المرور: {e}")
    
    def login(self):
        """محاولة تسجيل الدخول"""
        try:
            username = self.username_input.text().strip()
            password = self.password_input.text().strip()
            
            # التحقق من وجود كلمة المرور
            if not password:
                self.show_error("يرجى إدخال كلمة المرور")
                return
            
            # محاولة المصادقة
            if auth_manager.authenticate(username, password):
                # تسجيل دخول ناجح
                self.login_successful.emit()
                self.accept()
            else:
                # تسجيل دخول فاشل
                self.login_attempts += 1
                
                if self.login_attempts >= self.max_attempts:
                    self.show_error(f"تم تجاوز عدد المحاولات المسموح ({self.max_attempts})")
                    auth_logger.log_security_event("تجاوز عدد محاولات تسجيل الدخول", username)
                    QTimer.singleShot(3000, self.reject)  # إغلاق النافذة بعد 3 ثواني
                else:
                    remaining = self.max_attempts - self.login_attempts
                    self.show_error(f"كلمة مرور خاطئة. المحاولات المتبقية: {remaining}")
                
                # تنظيف حقل كلمة المرور
                self.password_input.clear()
                self.password_input.setFocus()
                
        except Exception as e:
            logging.error(f"خطأ في تسجيل الدخول: {e}")
            self.show_error("حدث خطأ في تسجيل الدخول")
    
    def show_error(self, message: str):
        """عرض رسالة خطأ"""
        try:
            self.error_label.setText(message)
            self.error_label.show()
            
            # إخفاء الرسالة بعد 5 ثواني
            QTimer.singleShot(5000, self.error_label.hide)
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة الخطأ: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات النافذة"""
        try:
            style = """
                QDialog {
                    background-color: #ECF0F1;
                    font-family: 'Segoe UI', Tahoma, Arial;
                }
                
                #headerFrame {
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                    border: 1px solid #BDC3C7;
                }
                
                #titleLabel {
                    font-size: 20px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin: 10px 0 5px 0;
                }
                
                #subtitleLabel {
                    font-size: 12px;
                    color: #7F8C8D;
                    margin-bottom: 10px;
                }
                
                #formFrame {
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                    border: 1px solid #BDC3C7;
                }
                
                #fieldLabel {
                    font-size: 12px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 5px;
                }
                
                #passwordInput {
                    padding: 12px;
                    border: 2px solid #BDC3C7;
                    border-radius: 6px;
                    font-size: 14px;
                    background-color: white;
                }
                
                #passwordInput:focus {
                    border-color: #3498DB;
                    outline: none;
                }
                
                #showPasswordCheckbox {
                    font-size: 11px;
                    color: #7F8C8D;
                    margin-top: 5px;
                }
                
                #errorLabel {
                    color: #E74C3C;
                    font-size: 12px;
                    font-weight: bold;
                    margin-top: 10px;
                    padding: 8px;
                    background-color: #FADBD8;
                    border: 1px solid #E74C3C;
                    border-radius: 4px;
                }
                
                #loginButton {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 120px;
                }
                
                #loginButton:hover {
                    background-color: #2980B9;
                }
                
                #loginButton:pressed {
                    background-color: #21618C;
                }
                
                #cancelButton {
                    background-color: #95A5A6;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 80px;
                }
                
                #cancelButton:hover {
                    background-color: #7F8C8D;
                }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التنسيقات: {e}")
    
    def keyPressEvent(self, event):
        """معالجة ضغط المفاتيح"""
        try:
            if event.key() == Qt.Key_Escape:
                self.reject()
            elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
                self.login()
            else:
                super().keyPressEvent(event)
                
        except Exception as e:
            logging.error(f"خطأ في معالجة ضغط المفاتيح: {e}")
            super().keyPressEvent(event)
    
    def closeEvent(self, event):
        """معالجة إغلاق النافذة"""
        try:
            auth_logger.log_security_event("تم إلغاء تسجيل الدخول")
            event.accept()
            
        except Exception as e:
            logging.error(f"خطأ في إغلاق نافذة تسجيل الدخول: {e}")
            event.accept()
