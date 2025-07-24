#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة لوحة التحكم الرئيسية
"""

import logging
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QFrame, QLabel, QPushButton, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap

from core.database.connection import db_manager
from core.utils.logger import log_user_action


class DashboardPage(QWidget):
    """صفحة لوحة التحكم"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_styles()
        self.load_statistics()
        
        # تحديث الإحصائيات كل 5 دقائق
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.load_statistics)
        self.refresh_timer.start(300000)  # 5 دقائق
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(20, 20, 20, 20)
            main_layout.setSpacing(20)
            
            # رسالة الترحيب
            self.create_welcome_section(main_layout)
            
            # إحصائيات سريعة
            self.create_statistics_section(main_layout)
            
            # الإجراءات السريعة
            self.create_quick_actions_section(main_layout)
            
            # معلومات النظام
            self.create_system_info_section(main_layout)
            
            # مساحة مرنة
            main_layout.addStretch()
            
            self.setLayout(main_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة لوحة التحكم: {e}")
            raise
    
    def create_welcome_section(self, layout):
        """إنشاء قسم الترحيب"""
        try:
            welcome_frame = QFrame()
            welcome_frame.setObjectName("welcomeFrame")
            
            welcome_layout = QVBoxLayout(welcome_frame)
            welcome_layout.setAlignment(Qt.AlignCenter)
            welcome_layout.setContentsMargins(30, 30, 30, 30)
            
            # عنوان الترحيب
            welcome_title = QLabel("مرحباً بك في نظام حسابات المدارس الأهلية")
            welcome_title.setObjectName("welcomeTitle")
            welcome_title.setAlignment(Qt.AlignCenter)
            welcome_layout.addWidget(welcome_title)
            
            # نص الترحيب
            welcome_text = QLabel("إدارة شاملة ومتقدمة لحسابات المدارس الأهلية")
            welcome_text.setObjectName("welcomeText")
            welcome_text.setAlignment(Qt.AlignCenter)
            welcome_layout.addWidget(welcome_text)
            
            layout.addWidget(welcome_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الترحيب: {e}")
            raise
    
    def create_statistics_section(self, layout):
        """إنشاء قسم الإحصائيات السريعة"""
        try:
            stats_frame = QFrame()
            stats_frame.setObjectName("statsFrame")
            
            stats_layout = QVBoxLayout(stats_frame)
            stats_layout.setContentsMargins(20, 20, 20, 20)
            
            # عنوان القسم
            stats_title = QLabel("الإحصائيات السريعة")
            stats_title.setObjectName("sectionTitle")
            stats_layout.addWidget(stats_title)
            
            # شبكة الإحصائيات
            stats_grid = QGridLayout()
            stats_grid.setSpacing(15)
            
            # إنشاء بطاقات الإحصائيات
            self.schools_card = self.create_stat_card("المدارس", "0", "#3498DB")
            self.students_card = self.create_stat_card("الطلاب", "0", "#27AE60")
            self.total_fees_card = self.create_stat_card("إجمالي الأقساط", "0 د.ع", "#F39C12")
            self.paid_fees_card = self.create_stat_card("المبالغ المدفوعة", "0 د.ع", "#2ECC71")
            self.remaining_fees_card = self.create_stat_card("المبالغ المتبقية", "0 د.ع", "#E74C3C")
            self.additional_fees_card = self.create_stat_card("الرسوم الإضافية", "0 د.ع", "#9B59B6")
            
            # ترتيب البطاقات في الشبكة
            stats_grid.addWidget(self.schools_card, 0, 0)
            stats_grid.addWidget(self.students_card, 0, 1)
            stats_grid.addWidget(self.total_fees_card, 0, 2)
            stats_grid.addWidget(self.paid_fees_card, 1, 0)
            stats_grid.addWidget(self.remaining_fees_card, 1, 1)
            stats_grid.addWidget(self.additional_fees_card, 1, 2)
            
            stats_layout.addLayout(stats_grid)
            layout.addWidget(stats_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الإحصائيات: {e}")
            raise
    
    def create_stat_card(self, title: str, value: str, color: str):
        """إنشاء بطاقة إحصائية"""
        try:
            card = QFrame()
            card.setObjectName("statCard")
            card.setFixedHeight(100)
            
            layout = QVBoxLayout(card)
            layout.setAlignment(Qt.AlignCenter)
            layout.setContentsMargins(15, 15, 15, 15)
            
            # القيمة
            value_label = QLabel(value)
            value_label.setObjectName("statValue")
            value_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(value_label)
            
            # العنوان
            title_label = QLabel(title)
            title_label.setObjectName("statTitle")
            title_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(title_label)
            
            # تطبيق اللون
            card.setStyleSheet(f"""
                #statCard {{
                    background-color: {color};
                    border-radius: 8px;
                    border: none;
                }}
                #statValue {{
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                }}
                #statTitle {{
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                }}
            """)
            
            return card
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء بطاقة الإحصائية: {e}")
            return QFrame()
    
    def create_quick_actions_section(self, layout):
        """إنشاء قسم الإجراءات السريعة"""
        try:
            actions_frame = QFrame()
            actions_frame.setObjectName("actionsFrame")
            
            actions_layout = QVBoxLayout(actions_frame)
            actions_layout.setContentsMargins(20, 20, 20, 20)
            
            # عنوان القسم
            actions_title = QLabel("الإجراءات السريعة")
            actions_title.setObjectName("sectionTitle")
            actions_layout.addWidget(actions_title)
            
            # أزرار الإجراءات
            buttons_layout = QHBoxLayout()
            buttons_layout.setSpacing(15)
            
            # زر إضافة مدرسة
            add_school_btn = QPushButton("إضافة مدرسة جديدة")
            add_school_btn.setObjectName("actionButton")
            add_school_btn.clicked.connect(self.add_school_action)
            buttons_layout.addWidget(add_school_btn)
            
            # زر إضافة طالب
            add_student_btn = QPushButton("إضافة طالب جديد")
            add_student_btn.setObjectName("actionButton")
            add_student_btn.clicked.connect(self.add_student_action)
            buttons_layout.addWidget(add_student_btn)
            
            # زر إضافة قسط
            add_payment_btn = QPushButton("تسجيل دفعة")
            add_payment_btn.setObjectName("actionButton")
            add_payment_btn.clicked.connect(self.add_payment_action)
            buttons_layout.addWidget(add_payment_btn)
            
            # زر التقارير
            reports_btn = QPushButton("عرض التقارير")
            reports_btn.setObjectName("actionButton")
            reports_btn.clicked.connect(self.view_reports_action)
            buttons_layout.addWidget(reports_btn)
            
            actions_layout.addLayout(buttons_layout)
            layout.addWidget(actions_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الإجراءات السريعة: {e}")
            raise
    
    def create_system_info_section(self, layout):
        """إنشاء قسم معلومات النظام"""
        try:
            info_frame = QFrame()
            info_frame.setObjectName("infoFrame")
            
            info_layout = QVBoxLayout(info_frame)
            info_layout.setContentsMargins(20, 20, 20, 20)
            
            # عنوان القسم
            info_title = QLabel("معلومات النظام")
            info_title.setObjectName("sectionTitle")
            info_layout.addWidget(info_title)
            
            # معلومات النظام
            info_grid = QGridLayout()
            info_grid.setSpacing(10)
            
            # تاريخ آخر تحديث
            self.last_update_label = QLabel("آخر تحديث: جاري التحميل...")
            self.last_update_label.setObjectName("infoLabel")
            info_grid.addWidget(QLabel("آخر تحديث:"), 0, 0)
            info_grid.addWidget(self.last_update_label, 0, 1)
            
            # حالة قاعدة البيانات
            self.db_status_label = QLabel("متصل")
            self.db_status_label.setObjectName("infoLabel")
            info_grid.addWidget(QLabel("حالة قاعدة البيانات:"), 1, 0)
            info_grid.addWidget(self.db_status_label, 1, 1)
            
            # حالة النسخ الاحتياطي
            self.backup_status_label = QLabel("غير مفعل")
            self.backup_status_label.setObjectName("infoLabel")
            info_grid.addWidget(QLabel("النسخ الاحتياطي:"), 2, 0)
            info_grid.addWidget(self.backup_status_label, 2, 1)
            
            info_layout.addLayout(info_grid)
            layout.addWidget(info_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم معلومات النظام: {e}")
            raise
    
    def load_statistics(self):
        """تحميل الإحصائيات من قاعدة البيانات"""
        try:
            # إحصائيات المدارس
            schools_count = self.get_schools_count()
            self.update_stat_card(self.schools_card, str(schools_count))
            
            # إحصائيات الطلاب
            students_count = self.get_students_count()
            self.update_stat_card(self.students_card, str(students_count))
            
            # إحصائيات الأقساط
            total_fees, paid_fees, remaining_fees = self.get_fees_statistics()
            self.update_stat_card(self.total_fees_card, f"{total_fees:,.0f} د.ع")
            self.update_stat_card(self.paid_fees_card, f"{paid_fees:,.0f} د.ع")
            self.update_stat_card(self.remaining_fees_card, f"{remaining_fees:,.0f} د.ع")
            
            # إحصائيات الرسوم الإضافية
            additional_fees = self.get_additional_fees_total()
            self.update_stat_card(self.additional_fees_card, f"{additional_fees:,.0f} د.ع")
            
            # تحديث معلومات النظام
            self.update_system_info()
            
            log_user_action("تم تحديث إحصائيات لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الإحصائيات: {e}")
    
    def get_schools_count(self) -> int:
        """الحصول على عدد المدارس"""
        try:
            query = "SELECT COUNT(*) as count FROM schools"
            result = db_manager.execute_query(query)
            return result[0]['count'] if result else 0
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على عدد المدارس: {e}")
            return 0
    
    def get_students_count(self) -> int:
        """الحصول على عدد الطلاب"""
        try:
            query = "SELECT COUNT(*) as count FROM students"
            result = db_manager.execute_query(query)
            return result[0]['count'] if result else 0
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على عدد الطلاب: {e}")
            return 0
    
    def get_fees_statistics(self) -> tuple:
        """الحصول على إحصائيات الأقساط"""
        try:
            # إجمالي الأقساط
            total_query = "SELECT SUM(total_fee) as total FROM students"
            total_result = db_manager.execute_query(total_query)
            total_fees = total_result[0]['total'] if total_result and total_result[0]['total'] else 0
            
            # المبالغ المدفوعة
            paid_query = "SELECT SUM(amount) as paid FROM installments"
            paid_result = db_manager.execute_query(paid_query)
            paid_fees = paid_result[0]['paid'] if paid_result and paid_result[0]['paid'] else 0
            
            # المبالغ المتبقية
            remaining_fees = total_fees - paid_fees
            
            return float(total_fees), float(paid_fees), float(remaining_fees)
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على إحصائيات الأقساط: {e}")
            return 0.0, 0.0, 0.0
    
    def get_additional_fees_total(self) -> float:
        """الحصول على إجمالي الرسوم الإضافية"""
        try:
            query = "SELECT SUM(amount) as total FROM additional_fees WHERE paid = 1"
            result = db_manager.execute_query(query)
            return float(result[0]['total']) if result and result[0]['total'] else 0.0
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على إجمالي الرسوم الإضافية: {e}")
            return 0.0
    
    def update_stat_card(self, card: QFrame, value: str):
        """تحديث قيمة بطاقة الإحصائية"""
        try:
            # العثور على label القيمة وتحديثه
            value_label = card.findChild(QLabel, "statValue")
            if value_label:
                value_label.setText(value)
                
        except Exception as e:
            logging.error(f"خطأ في تحديث بطاقة الإحصائية: {e}")
    
    def update_system_info(self):
        """تحديث معلومات النظام"""
        try:
            from datetime import datetime
            
            # تحديث وقت آخر تحديث
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.last_update_label.setText(current_time)
            
            # التحقق من حالة قاعدة البيانات
            try:
                db_manager.execute_query("SELECT 1")
                self.db_status_label.setText("متصل")
                self.db_status_label.setStyleSheet("color: #27AE60;")
            except:
                self.db_status_label.setText("غير متصل")
                self.db_status_label.setStyleSheet("color: #E74C3C;")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث معلومات النظام: {e}")
    
    def add_school_action(self):
        """إجراء إضافة مدرسة"""
        try:
            # إرسال إشارة للنافذة الرئيسية للانتقال إلى صفحة المدارس
            from PyQt5.QtWidgets import QApplication
            main_window = QApplication.activeWindow()
            if main_window and hasattr(main_window, 'navigate_to_page'):
                main_window.navigate_to_page('schools')
            
            log_user_action("طلب إضافة مدرسة من لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في إجراء إضافة مدرسة: {e}")
    
    def add_student_action(self):
        """إجراء إضافة طالب"""
        try:
            from PyQt5.QtWidgets import QApplication
            main_window = QApplication.activeWindow()
            if main_window and hasattr(main_window, 'navigate_to_page'):
                main_window.navigate_to_page('students')
            
            log_user_action("طلب إضافة طالب من لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في إجراء إضافة طالب: {e}")
    
    def add_payment_action(self):
        """إجراء إضافة دفعة"""
        try:
            from PyQt5.QtWidgets import QApplication
            main_window = QApplication.activeWindow()
            if main_window and hasattr(main_window, 'navigate_to_page'):
                main_window.navigate_to_page('installments')
            
            log_user_action("طلب تسجيل دفعة من لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في إجراء إضافة دفعة: {e}")
    
    def view_reports_action(self):
        """إجراء عرض التقارير"""
        try:
            from PyQt5.QtWidgets import QApplication
            main_window = QApplication.activeWindow()
            if main_window and hasattr(main_window, 'navigate_to_page'):
                main_window.navigate_to_page('reports')
            
            log_user_action("طلب عرض التقارير من لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في إجراء عرض التقارير: {e}")
    
    def refresh(self):
        """تحديث الصفحة"""
        try:
            self.load_statistics()
            log_user_action("تم تحديث لوحة التحكم")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث لوحة التحكم: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات الصفحة"""
        try:
            style = """
                #welcomeFrame {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1,
                                              stop: 0 #3498DB, stop: 1 #2980B9);
                    border-radius: 12px;
                    margin-bottom: 10px;
                }
                
                #welcomeTitle {
                    color: white;
                    font-size: 24px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                
                #welcomeText {
                    color: #ECF0F1;
                    font-size: 14px;
                    margin-bottom: 10px;
                }
                
                #statsFrame, #actionsFrame, #infoFrame {
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 8px;
                    margin-bottom: 15px;
                }
                
                #sectionTitle {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 15px;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #ECF0F1;
                }
                
                #actionButton {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    padding: 12px 20px;
                    border-radius: 6px;
                    font-size: 13px;
                    font-weight: bold;
                    min-width: 150px;
                }
                
                #actionButton:hover {
                    background-color: #2980B9;
                }
                
                #actionButton:pressed {
                    background-color: #21618C;
                }
                
                #infoLabel {
                    color: #7F8C8D;
                    font-size: 12px;
                }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد تنسيقات الصفحة: {e}")
