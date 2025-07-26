#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة تفاصيل الطالب - عرض شامل لمعلومات الطالب والأقساط والرسوم الإضافية
"""

import logging
from datetime import datetime, date, time
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QGroupBox, QGridLayout, QScrollArea, QMessageBox, QDialog,
    QLineEdit, QDateEdit, QTimeEdit, QTextEdit, QSpinBox,
    QTabWidget, QSplitter
)
from PyQt5.QtCore import Qt, QDate, QTime, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation
from .add_installment_dialog import AddInstallmentDialog
from .add_additional_fee_dialog import AddAdditionalFeeDialog


class StudentDetailsPage(QWidget):
    """صفحة تفاصيل الطالب الشاملة"""
    
    # إشارات النافذة
    back_requested = pyqtSignal()
    student_updated = pyqtSignal()
    
    def __init__(self, student_id):
        super().__init__()
        self.student_id = student_id
        self.student_data = None
        self.installments_data = []
        self.additional_fees_data = []
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_student_data()
        
        log_user_action(f"فتح صفحة تفاصيل الطالب: {student_id}")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي مع إمكانية التمرير
            main_layout = QVBoxLayout()
            main_layout.setContentsMargins(10, 10, 10, 10)
            main_layout.setSpacing(10)
            
            # شريط الرجوع
            self.create_back_toolbar(main_layout)
            
            # منطقة التمرير
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            
            # المحتوى الرئيسي
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setContentsMargins(5, 5, 5, 5)
            content_layout.setSpacing(15)
            
            # معلومات الطالب الأساسية
            self.create_student_info_section(content_layout)
            
            # التقسيم الأفقي للأقساط والرسوم
            splitter = QSplitter(Qt.Horizontal)
            
            # قسم الأقساط
            installments_widget = self.create_installments_section()
            splitter.addWidget(installments_widget)
            
            # قسم الرسوم الإضافية
            fees_widget = self.create_additional_fees_section()
            splitter.addWidget(fees_widget)
            
            # تعيين النسب
            splitter.setSizes([400, 300])
            content_layout.addWidget(splitter)
            
            scroll_area.setWidget(content_widget)
            main_layout.addWidget(scroll_area)
            
            self.setLayout(main_layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة تفاصيل الطالب: {e}")
            raise
    
    def create_back_toolbar(self, layout):
        """إنشاء شريط الرجوع"""
        try:
            toolbar_frame = QFrame()
            toolbar_frame.setObjectName("backToolbar")
            
            toolbar_layout = QHBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(15, 10, 15, 10)
            
            # زر الرجوع
            self.back_button = QPushButton("← رجوع")
            self.back_button.setObjectName("backButton")
            toolbar_layout.addWidget(self.back_button)
            
            # عنوان الصفحة
            self.page_title = QLabel("تفاصيل الطالب")
            self.page_title.setObjectName("pageTitle")
            self.page_title.setAlignment(Qt.AlignCenter)
            self.page_title.setStyleSheet("color: black;")
            toolbar_layout.addWidget(self.page_title)
            
            # زر التحديث
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("refreshButton")
            toolbar_layout.addWidget(self.refresh_button)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الرجوع: {e}")
            raise
    
    def create_student_info_section(self, layout):
        """إنشاء قسم معلومات الطالب"""
        try:
            info_frame = QFrame()
            info_frame.setObjectName("studentInfoFrame")
            
            info_layout = QVBoxLayout(info_frame)
            info_layout.setContentsMargins(20, 15, 20, 15)
            
            # عنوان القسم
            title_label = QLabel("معلومات الطالب")
            title_label.setObjectName("sectionTitle")
            info_layout.addWidget(title_label)
            
            # شبكة المعلومات
            grid_layout = QGridLayout()
            grid_layout.setSpacing(15)
            
            # تسميات المعلومات
            self.name_label = QLabel("--")
            self.name_label.setObjectName("studentName")
            
            self.school_label = QLabel("--")
            self.school_label.setObjectName("infoValue")
            
            self.grade_label = QLabel("--")
            self.grade_label.setObjectName("infoValue")
            
            self.section_label = QLabel("--")
            self.section_label.setObjectName("infoValue")
            
            self.gender_label = QLabel("--")
            self.gender_label.setObjectName("infoValue")
            
            self.phone_label = QLabel("--")
            self.phone_label.setObjectName("infoValue")
            
            self.status_label = QLabel("--")
            self.status_label.setObjectName("infoValue")
            
            self.start_date_label = QLabel("--")
            self.start_date_label.setObjectName("infoValue")
            
            # إضافة المعلومات للشبكة
            grid_layout.addWidget(QLabel("الاسم:"), 0, 0)
            grid_layout.addWidget(self.name_label, 0, 1)
            grid_layout.addWidget(QLabel("المدرسة:"), 0, 2)
            grid_layout.addWidget(self.school_label, 0, 3)
            
            grid_layout.addWidget(QLabel("الصف:"), 1, 0)
            grid_layout.addWidget(self.grade_label, 1, 1)
            grid_layout.addWidget(QLabel("الشعبة:"), 1, 2)
            grid_layout.addWidget(self.section_label, 1, 3)
            
            grid_layout.addWidget(QLabel("الجنس:"), 2, 0)
            grid_layout.addWidget(self.gender_label, 2, 1)
            grid_layout.addWidget(QLabel("الهاتف:"), 2, 2)
            grid_layout.addWidget(self.phone_label, 2, 3)
            
            grid_layout.addWidget(QLabel("الحالة:"), 3, 0)
            grid_layout.addWidget(self.status_label, 3, 1)
            grid_layout.addWidget(QLabel("تاريخ المباشرة:"), 3, 2)
            grid_layout.addWidget(self.start_date_label, 3, 3)
            
            info_layout.addLayout(grid_layout)
            
            # ملخص مالي
            self.create_financial_summary(info_layout)
            
            layout.addWidget(info_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم معلومات الطالب: {e}")
            raise
    
    def create_financial_summary(self, layout):
        """إنشاء ملخص مالي للطالب"""
        try:
            summary_frame = QFrame()
            summary_frame.setObjectName("financialSummary")
            
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(15, 10, 15, 10)
            
            # القسط الكلي
            self.total_fee_label = QLabel("القسط الكلي: 0 د.ع")
            self.total_fee_label.setObjectName("totalFee")
            summary_layout.addWidget(self.total_fee_label)
            
            # المدفوع
            self.paid_amount_label = QLabel("المدفوع: 0 د.ع")
            self.paid_amount_label.setObjectName("paidAmount")
            summary_layout.addWidget(self.paid_amount_label)
            
            # المتبقي
            self.remaining_amount_label = QLabel("المتبقي: 0 د.ع")
            self.remaining_amount_label.setObjectName("remainingAmount")
            summary_layout.addWidget(self.remaining_amount_label)
            
            # عدد الدفعات
            self.installments_count_label = QLabel("عدد الدفعات: 0")
            self.installments_count_label.setObjectName("installmentsCount")
            summary_layout.addWidget(self.installments_count_label)
            
            layout.addWidget(summary_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الملخص المالي: {e}")
            raise
    
    def create_installments_section(self):
        """إنشاء قسم الأقساط"""
        try:
            installments_widget = QWidget()
            installments_layout = QVBoxLayout(installments_widget)
            installments_layout.setContentsMargins(10, 10, 10, 10)
            
            # رأس القسم
            header_layout = QHBoxLayout()
            
            title_label = QLabel("الأقساط المدفوعة")
            title_label.setObjectName("sectionTitle")
            header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            
            # زر إضافة قسط
            self.add_installment_button = QPushButton("+ إضافة قسط")
            self.add_installment_button.setObjectName("addButton")
            header_layout.addWidget(self.add_installment_button)
            
            installments_layout.addLayout(header_layout)
            
            # جدول الأقساط
            self.installments_table = QTableWidget()
            self.installments_table.setObjectName("dataTable")
            self.installments_table.setStyleSheet("QTableWidget::item { padding: 0px; }")  # إزالة الحشو لإظهار أزرار الإجراءات بشكل صحيح
            
            # إعداد أعمدة الجدول
            columns = ["المبلغ", "التاريخ", "وقت الدفع", "الملاحظات", "إجراءات"]
            self.installments_table.setColumnCount(len(columns))
            self.installments_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.installments_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.installments_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.installments_table.setAlternatingRowColors(True)
            
            # إعداد حجم الأعمدة
            header = self.installments_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # المبلغ
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # التاريخ
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # وقت الدفع
            header.setSectionResizeMode(3, QHeaderView.Stretch)          # الملاحظات
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # الإجراءات
            
            installments_layout.addWidget(self.installments_table)
            
            return installments_widget
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الأقساط: {e}")
            raise
    
    def create_additional_fees_section(self):
        """إنشاء قسم الرسوم الإضافية"""
        try:
            fees_widget = QWidget()
            fees_layout = QVBoxLayout(fees_widget)
            fees_layout.setContentsMargins(10, 10, 10, 10)
            
            # رأس القسم
            header_layout = QHBoxLayout()
            
            title_label = QLabel("الرسوم الإضافية")
            title_label.setObjectName("sectionTitle")
            header_layout.addWidget(title_label)
            
            header_layout.addStretch()
            
            # زر إضافة رسم
            self.add_fee_button = QPushButton("+ إضافة رسم")
            self.add_fee_button.setObjectName("addButton")
            header_layout.addWidget(self.add_fee_button)
            
            fees_layout.addLayout(header_layout)
            
            # جدول الرسوم الإضافية
            self.fees_table = QTableWidget()
            self.fees_table.setObjectName("dataTable")
            self.fees_table.setStyleSheet("QTableWidget::item { padding: 0px; }")  # إزالة الحشو لإظهار أزرار الإجراءات بشكل صحيح
            
            # إعداد أعمدة الجدول
            columns = ["النوع", "المبلغ", "تاريخ الإضافة", "تاريخ الدفع", "إجراءات"]
            self.fees_table.setColumnCount(len(columns))
            self.fees_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.fees_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.fees_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.fees_table.setAlternatingRowColors(True)
            
            # إعداد حجم الأعمدة
            header = self.fees_table.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # النوع
            header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # المبلغ
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # تاريخ الإضافة
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # تاريخ الدفع
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # الإجراءات
            
            fees_layout.addWidget(self.fees_table)
            
            return fees_widget
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء قسم الرسوم الإضافية: {e}")
            raise
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            # أزرار العمليات
            self.back_button.clicked.connect(self.back_requested.emit)
            self.refresh_button.clicked.connect(self.refresh_data)
            self.add_installment_button.clicked.connect(self.add_installment)
            self.add_fee_button.clicked.connect(self.add_additional_fee)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def load_student_data(self):
        """تحميل بيانات الطالب"""
        try:
            # تحميل المعلومات الأساسية
            query = """
                SELECT s.*, sc.name_ar as school_name
                FROM students s
                LEFT JOIN schools sc ON s.school_id = sc.id
                WHERE s.id = ?
            """
            result = db_manager.execute_query(query, (self.student_id,))
            
            if result:
                self.student_data = result[0]
                self.update_student_info()
                self.load_installments()
                self.load_additional_fees()
                self.update_financial_summary()
            else:
                # بيانات افتراضية للاختبار
                self.student_data = None
                self.installments_data = []
                self.additional_fees_data = []
                
                # عرض رسالة تحذير فقط في حالة عدم العثور على بيانات حقيقية
                if hasattr(self, 'parent') and self.parent():
                    QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات الطالب")
                
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الطالب: {e}")
            self.student_data = None
            self.installments_data = []
            self.additional_fees_data = []
            
            # عرض رسالة خطأ فقط في حالة وجود واجهة مستخدم
            if hasattr(self, 'parent') and self.parent():
                QMessageBox.critical(self, "خطأ", f"خطأ في تحميل البيانات: {str(e)}")
    
    def update_student_info(self):
        """تحديث معلومات الطالب في الواجهة"""
        try:
            if not self.student_data:
                # قيم افتراضية في حالة عدم وجود بيانات
                self.page_title.setText("تفاصيل الطالب")
                self.name_label.setText("--")
                self.school_label.setText("--")
                self.grade_label.setText("--")
                self.section_label.setText("--")
                self.gender_label.setText("--")
                self.phone_label.setText("--")
                self.status_label.setText("--")
                self.start_date_label.setText("--")
                self.total_fee_label.setText("القسط الكلي: 0 د.ع")
                return
            
            # التحقق من طول البيانات
            if len(self.student_data) < 16:
                logging.warning(f"بيانات الطالب غير مكتملة: {len(self.student_data)} حقل")
                return
            
            # تحديث العنوان - استخدام اسم الحقل الصحيح
            student_name = str(self.student_data[1])  # name هو الحقل الثاني
            self.page_title.setText(f"تفاصيل الطالب: {student_name}")
            
            # تحديث المعلومات باستخدام المؤشرات الصحيحة
            self.name_label.setText(student_name)
            self.school_label.setText(str(self.student_data[-1] or "--"))  # school_name هو الحقل الأخير
            self.grade_label.setText(str(self.student_data[4]))  # grade - الحقل رقم 4
            self.section_label.setText(str(self.student_data[5]))  # section - الحقل رقم 5
            self.gender_label.setText(str(self.student_data[7]))  # gender - الحقل رقم 7
            self.phone_label.setText(str(self.student_data[8] or "--"))  # phone - الحقل رقم 8
            self.status_label.setText(str(self.student_data[13]))  # status - الحقل رقم 13
            self.start_date_label.setText(str(self.student_data[12]))  # start_date - الحقل رقم 12
            
            # تحديث القسط الكلي - total_fee هو الحقل رقم 11
            try:
                total_fee = float(self.student_data[11])
                self.total_fee_label.setText(f"القسط الكلي: {total_fee:,.0f} د.ع")
            except (ValueError, TypeError):
                logging.error(f"خطأ في تحويل القسط الكلي: {self.student_data[11]}")
                self.total_fee_label.setText("القسط الكلي: 0 د.ع")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث معلومات الطالب: {e}")
            # قيم افتراضية في حالة الخطأ
            self.page_title.setText("تفاصيل الطالب")
            self.name_label.setText("--")
            self.school_label.setText("--")
            self.grade_label.setText("--")
            self.section_label.setText("--")
            self.gender_label.setText("--")
            self.phone_label.setText("--")
            self.status_label.setText("--")
            self.start_date_label.setText("--")
            self.total_fee_label.setText("القسط الكلي: 0 د.ع")
    
    def load_installments(self):
        """تحميل الأقساط المدفوعة"""
        try:
            query = """
                SELECT id, amount, payment_date, payment_time, notes
                FROM installments 
                WHERE student_id = ?
                ORDER BY payment_date DESC
            """
            self.installments_data = db_manager.execute_query(query, (self.student_id,))
            self.update_installments_table()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الأقساط: {e}")
    
    def update_installments_table(self):
        """تحديث جدول الأقساط"""
        try:
            self.installments_table.setRowCount(len(self.installments_data))
            
            for row, installment in enumerate(self.installments_data):
                # المبلغ
                amount_value = float(installment[1]) if installment and len(installment) > 1 else 0
                amount_item = QTableWidgetItem(f"{amount_value:,.0f} د.ع")
                self.installments_table.setItem(row, 0, amount_item)
                
                # التاريخ
                date_item = QTableWidgetItem(str(installment[2] or ""))
                self.installments_table.setItem(row, 1, date_item)
                
                # وقت الدفع
                time_item = QTableWidgetItem(str(installment[3] or "--"))
                self.installments_table.setItem(row, 2, time_item)
                
                # الملاحظات
                notes_item = QTableWidgetItem(str(installment[4] or ""))
                self.installments_table.setItem(row, 3, notes_item)
                
                # أزرار الإجراءات
                actions_layout = QHBoxLayout()
                actions_widget = QWidget()
                
                delete_btn = QPushButton("حذف")
                delete_btn.setObjectName("deleteButton")
                delete_btn.clicked.connect(lambda checked, id=installment[0]: self.delete_installment(id))
                actions_layout.addWidget(delete_btn)
                
                actions_widget.setLayout(actions_layout)
                self.installments_table.setCellWidget(row, 4, actions_widget)
            
        except Exception as e:
            logging.error(f"خطأ في تحديث جدول الأقساط: {e}")
    
    def update_financial_summary(self):
        """تحديث الملخص المالي"""
        try:
            if not self.student_data or len(self.student_data) < 12:
                # قيم افتراضية في حالة عدم وجود بيانات
                self.total_fee_label.setText("القسط الكلي: 0 د.ع")
                self.paid_amount_label.setText("المدفوع: 0 د.ع")
                self.remaining_amount_label.setText("المتبقي: 0 د.ع")
                self.installments_count_label.setText("عدد الدفعات: 0")
                return
            
            # حساب المبلغ المدفوع من الأقساط
            total_paid = 0
            for installment in self.installments_data:
                try:
                    # استخدام المبلغ المدفوع إذا كان موجود، وإلا استخدم المبلغ الكامل
                    paid_amount = installment[6] if len(installment) > 6 and installment[6] else installment[1]
                    total_paid += float(paid_amount)
                except (ValueError, TypeError, IndexError):
                    logging.warning(f"تجاهل قسط غير صحيح: {installment}")
                    continue
            
            # القسط الكلي - total_fee هو الحقل رقم 11
            try:
                total_fee = float(self.student_data[11])
            except (ValueError, TypeError):
                logging.error(f"خطأ في تحويل القسط الكلي: {self.student_data[11]}")
                total_fee = 0
            
            # المتبقي
            remaining = total_fee - total_paid
            
            # عدد الدفعات
            installments_count = len(self.installments_data)
            
            # تحديث التسميات
            self.total_fee_label.setText(f"القسط الكلي: {total_fee:,.0f} د.ع")
            self.paid_amount_label.setText(f"المدفوع: {total_paid:,.0f} د.ع")
            self.remaining_amount_label.setText(f"المتبقي: {remaining:,.0f} د.ع")
            self.installments_count_label.setText(f"عدد الدفعات: {installments_count}")
            
            # تلوين المتبقي
            if remaining > 0:
                self.remaining_amount_label.setStyleSheet("color: #E74C3C; font-weight: bold;")
            else:
                self.remaining_amount_label.setStyleSheet("color: #27AE60; font-weight: bold;")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الملخص المالي: {e}")
            # قيم افتراضية في حالة الخطأ
            self.total_fee_label.setText("القسط الكلي: 0 د.ع")
            self.paid_amount_label.setText("المدفوع: 0 د.ع")
            self.remaining_amount_label.setText("المتبقي: 0 د.ع")
            self.installments_count_label.setText("عدد الدفعات: 0")
    
    def add_installment(self):
        """إضافة قسط جديد"""
        try:
            if not self.student_data or len(self.student_data) < 12:
                QMessageBox.warning(self, "خطأ", "لا توجد بيانات صحيحة للطالب")
                return
            
            # حساب المتبقي
            total_paid = 0
            for installment in self.installments_data:
                try:
                    # استخدام المبلغ المدفوع إذا كان موجود، وإلا استخدم المبلغ الكامل
                    paid_amount = installment[6] if len(installment) > 6 and installment[6] else installment[1]
                    total_paid += float(paid_amount)
                except (ValueError, TypeError, IndexError):
                    continue
            
            # القسط الكلي - total_fee هو الحقل رقم 11
            try:
                total_fee = float(self.student_data[11])
            except (ValueError, TypeError):
                QMessageBox.warning(self, "خطأ", "قيمة القسط الكلي غير صحيحة")
                return
            
            remaining = total_fee - total_paid
            
            if remaining <= 0:
                QMessageBox.information(self, "تنبيه", "تم دفع القسط بالكامل")
                return
            
            dialog = AddInstallmentDialog(self.student_id, remaining, self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_data()
                self.student_updated.emit()
                
        except Exception as e:
            logging.error(f"خطأ في إضافة قسط: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في إضافة القسط: {str(e)}")
    
    def load_additional_fees(self):
        """تحميل الرسوم الإضافية"""
        try:
            query = """
                SELECT id, fee_type, amount, paid, payment_date, added_at, notes
                FROM additional_fees
                WHERE student_id = ?
                ORDER BY added_at DESC
            """
            self.additional_fees_data = db_manager.execute_query(query, (self.student_id,))
            self.update_additional_fees_table()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الرسوم الإضافية: {e}")
    
    def update_additional_fees_table(self):
        """تحديث جدول الرسوم الإضافية"""
        try:
            self.fees_table.setRowCount(len(self.additional_fees_data))
            
            for row, fee in enumerate(self.additional_fees_data):
                # النوع
                type_item = QTableWidgetItem(str(fee[1]))
                self.fees_table.setItem(row, 0, type_item)
                
                # المبلغ
                amount_item = QTableWidgetItem(f"{float(fee[2]):,.0f} د.ع")
                self.fees_table.setItem(row, 1, amount_item)
                
                # تاريخ الإضافة
                date_item = QTableWidgetItem(str(fee[5] or "--"))
                self.fees_table.setItem(row, 2, date_item)
                
                # تاريخ الدفع
                payment_date_item = QTableWidgetItem(str(fee[4] or "--"))
                self.fees_table.setItem(row, 3, payment_date_item)
                
                # أزرار الإجراءات
                actions_layout = QHBoxLayout()
                actions_widget = QWidget()
                
                # إذا كان غير مدفوع، أضف زر الدفع
                is_paid = fee[3] if isinstance(fee[3], bool) else (fee[3] == 1 if fee[3] is not None else False)
                if not is_paid:
                    pay_btn = QPushButton("دفع")
                    pay_btn.setObjectName("payButton")
                    pay_btn.clicked.connect(lambda checked, id=fee[0]: self.pay_additional_fee(id))
                    actions_layout.addWidget(pay_btn)
                
                delete_btn = QPushButton("حذف")
                delete_btn.setObjectName("deleteButton")
                delete_btn.clicked.connect(lambda checked, id=fee[0]: self.delete_additional_fee(id))
                actions_layout.addWidget(delete_btn)
                
                actions_widget.setLayout(actions_layout)
                self.fees_table.setCellWidget(row, 4, actions_widget)
            
        except Exception as e:
            logging.error(f"خطأ في تحديث جدول الرسوم الإضافية: {e}")
    
    
    def add_additional_fee(self):
        """إضافة رسم إضافي"""
        try:
            dialog = AddAdditionalFeeDialog(self.student_id, self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_data()
                self.student_updated.emit()
                
        except Exception as e:
            logging.error(f"خطأ في إضافة رسم إضافي: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في إضافة الرسم: {str(e)}")
    
    def delete_installment(self, installment_id):
        """حذف قسط"""
        try:
            reply = QMessageBox.question(
                self, "تأكيد الحذف", 
                "هل أنت متأكد من حذف هذا القسط؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                query = "DELETE FROM installments WHERE id = ?"
                db_manager.execute_query(query, (installment_id,))
                
                log_database_operation(f"حذف قسط - معرف القسط: {installment_id}", "installments")
                log_user_action(f"حذف قسط للطالب: {self.student_id}")
                
                self.refresh_data()
                self.student_updated.emit()
                
                QMessageBox.information(self, "نجح", "تم حذف القسط بنجاح")
                
        except Exception as e:
            logging.error(f"خطأ في حذف القسط: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في حذف القسط: {str(e)}")
    
    def delete_additional_fee(self, fee_id):
        """حذف رسم إضافي"""
        try:
            reply = QMessageBox.question(
                self, "تأكيد الحذف", 
                "هل أنت متأكد من حذف هذا الرسم؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                query = "DELETE FROM additional_fees WHERE id = ?"
                db_manager.execute_query(query, (fee_id,))
                
                log_database_operation(f"حذف رسم إضافي - معرف الرسم: {fee_id}", "additional_fees")
                log_user_action(f"حذف رسم إضافي للطالب: {self.student_id}")
                
                self.refresh_data()
                self.student_updated.emit()
                
                QMessageBox.information(self, "نجح", "تم حذف الرسم بنجاح")
                
        except Exception as e:
            logging.error(f"خطأ في حذف الرسم الإضافي: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في حذف الرسم: {str(e)}")
    
    def pay_additional_fee(self, fee_id):
        """دفع رسم إضافي"""
        try:
            reply = QMessageBox.question(
                self, "تأكيد الدفع", 
                "هل تريد تسجيل هذا الرسم كمدفوع؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                current_date = date.today().strftime('%Y-%m-%d')
                
                # تحديث البيانات بالحقول الصحيحة
                query = """
                    UPDATE additional_fees 
                    SET paid = 1, payment_date = ?
                    WHERE id = ?
                """
                db_manager.execute_query(query, (current_date, fee_id))
                
                log_database_operation(f"دفع رسم إضافي - معرف الرسم: {fee_id}", "additional_fees")
                log_user_action(f"دفع رسم إضافي للطالب: {self.student_id}")
                
                self.refresh_data()
                self.student_updated.emit()
                
                QMessageBox.information(self, "نجح", "تم تسجيل الدفع بنجاح")
                
        except Exception as e:
            logging.error(f"خطأ في دفع الرسم الإضافي: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في تسجيل الدفع: {str(e)}")
    
    def refresh_data(self):
        """تحديث جميع البيانات"""
        try:
            self.load_student_data()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث البيانات: {e}")
    
    def setup_styles(self):
        """إعداد التنسيقات"""
        try:
            style = """
                /* الإطار الرئيسي */
                QWidget {
                    background-color: #F8F9FA;
                    font-family: 'Segoe UI', Tahoma, Arial;
                    font-size: 18px;
                }
                
                /* شريط الرجوع */
                #backToolbar {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2=1, 
                        stop:0 #3498DB, stop:1 #2980B9);
                    border-radius: 10px;
                    color: white;
                    margin-bottom: 10px;
                }
                
                #backButton {
                    background-color: #2980B9; /* لون أزرق داكن */
                    border: 2px solid #2471A3; /* حدود أغمق قليلاً */
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 18px;
                }
                
                #backButton:hover {
                    background-color: #2471A3; /* لون أغمق عند التحويم */
                    border-color: #1F618D; /* حدود أغمق عند التحويم */
                }
                
                #pageTitle {
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                }
                
                #refreshButton {
                    background-color: #2980B9; /* لون أزرق داكن */
                    border: 2px solid #2471A3; /* حدود أغمق قليلاً */
                    color: white;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 18px;
                }
                
                #refreshButton:hover {
                    background-color: #2471A3; /* لون أغمق عند التحويم */
                    border-color: #1F618D; /* حدود أغمق عند التحويم */
                }
                
                /* قسم معلومات الطالب */
                #studentInfoFrame {
                    background-color: white;
                    border: 1px solid #E0E0E0;
                    border-radius: 12px;
                    margin: 5px;
                }
                
                #sectionTitle {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 10px;
                    padding-bottom: 8px;
                    border-bottom: 2px solid #3498DB;
                }
                
                #studentName {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2C3E50;
                }
                
                #infoValue {
                    font-size: 18px;
                    color: #34495E;
                    background-color: #F8F9FA;
                    padding: 4px 8px;
                    border-radius: 4px;
                    border: 1px solid #E0E0E0;
                }
                
                /* الملخص المالي */
                #financialSummary {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                        stop:0 #ECF0F1, stop:1 #D5DBDB);
                    border: 1px solid #BDC3C7;
                    border-radius: 8px;
                    margin-top: 15px;
                }
                
                #totalFee {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    background-color: rgba(52, 152, 219, 0.1);
                    padding: 6px 12px;
                    border-radius: 6px;
                    border: 1px solid rgba(52, 152, 219, 0.3);
                }
                
                #paidAmount {
                    font-size: 18px;
                    font-weight: bold;
                    color: #27AE60;
                    background-color: rgba(39, 174, 96, 0.1);
                    padding: 6px 12px;
                    border-radius: 6px;
                    border: 1px solid rgba(39, 174, 96, 0.3);
                }
                
                #remainingAmount {
                    font-size: 18px;
                    font-weight: bold;
                    background-color: rgba(231, 76, 60, 0.1);
                    padding: 6px 12px;
                    border-radius: 6px;
                    border: 1px solid rgba(231, 76, 60, 0.3);
                }
                
                #installmentsCount {
                    font-size: 18px;
                    font-weight: bold;
                    color: #8E44AD;
                    background-color: rgba(142, 68, 173, 0.1);
                    padding: 6px 12px;
                    border-radius: 6px;
                    border: 1px solid rgba(142, 68, 173, 0.3);
                }
                
                /* الجداول */
                #dataTable {
                    background-color: white;
                    border: 1px solid #E0E0E0;
                    border-radius: 8px;
                    gridline-color: #F0F0F0;
                    font-size: 16px;
                }
                
                #dataTable::item {
                    padding: 8px;
                    border-bottom: 1px solid #F0F0F0;
                }
                
                #dataTable::item:selected {
                    background-color: #E3F2FD;
                    color: #1976D2;
                }
                
                #dataTable QHeaderView::section {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #F5F5F5, stop:1 #E8E8E8);
                    border: 1px solid #D0D0D0;
                    padding: 8px;
                    font-weight: bold;
                    color: #2C3E50;
                    font-size: 16px;
                }
                
                /* الأزرار */
                #addButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #27AE60, stop:1 #229954);
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 16px;
                }
                
                #addButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #229954, stop:1 #1E8449);
                }
                
                #deleteButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #E74C3C, stop:1 #C0392B);
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 14px;
                }
                
                #deleteButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #C0392B, stop:1 #A93226);
                }
                
                #payButton {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #F39C12, stop:1 #E67E22);
                    color: white;
                    border: none;
                    padding: 4px 8px;
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 14px;
                }
                
                #payButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1, 
                        stop:0 #E67E22, stop:1 #D35400);
                }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التنسيقات: {e}")
