#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة الأقساط
"""

import logging
import json
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QProgressBar, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation

# استيراد نافذة إضافة القسط
from .add_installment_dialog import AddInstallmentDialog


class InstallmentsPage(QWidget):
    """صفحة إدارة الأقساط"""
    
    # إشارات النافذة
    page_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_installments = []
        self.selected_school_id = None
        self.selected_student_id = None
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_initial_data()
        
        log_user_action("فتح صفحة إدارة الأقساط")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            # العنوان الرئيسي
            self.create_page_header(layout)
            
            # شريط الأدوات والفلاتر
            self.create_toolbar(layout)
            
            # جدول الأقساط
            self.create_installments_table(layout)
            
            # إحصائيات وملخص مالي
            self.create_financial_summary(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة الأقساط: {e}")
            raise
    
    def create_page_header(self, layout):
        """إنشاء رأس الصفحة"""
        try:
            header_frame = QFrame()
            header_frame.setObjectName("headerFrame")
            
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(20, 15, 20, 15)
            
            # العنوان والوصف
            text_layout = QVBoxLayout()
            
            title_label = QLabel("إدارة الأقساط")
            title_label.setObjectName("pageTitle")
            text_layout.addWidget(title_label)
            
            desc_label = QLabel("إدارة أقساط الطلاب والمدفوعات والمتابعة المالية")
            desc_label.setObjectName("pageDesc")
            text_layout.addWidget(desc_label)
            
            header_layout.addLayout(text_layout)
            header_layout.addStretch()
            
            # إحصائيات سريعة في الرأس
            stats_layout = QHBoxLayout()
            
            self.total_installments_label = QLabel("إجمالي الأقساط: 0")
            self.total_installments_label.setObjectName("quickStat")
            stats_layout.addWidget(self.total_installments_label)
            
            self.paid_amount_label = QLabel("المدفوع: 0 د.ع")
            self.paid_amount_label.setObjectName("quickStat")
            stats_layout.addWidget(self.paid_amount_label)
            
            self.pending_amount_label = QLabel("المستحق: 0 د.ع")
            self.pending_amount_label.setObjectName("quickStat")
            stats_layout.addWidget(self.pending_amount_label)
            
            header_layout.addLayout(stats_layout)
            
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس الصفحة: {e}")
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات والفلاتر"""
        try:
            toolbar_frame = QFrame()
            toolbar_frame.setObjectName("toolbarFrame")
            
            toolbar_layout = QVBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(15, 10, 15, 10)
            toolbar_layout.setSpacing(10)
            
            # الصف الأول - فلاتر أساسية
            filters_layout = QHBoxLayout()
            
            # اختيار المدرسة
            school_label = QLabel("المدرسة:")
            school_label.setObjectName("filterLabel")
            filters_layout.addWidget(school_label)
            
            self.school_combo = QComboBox()
            self.school_combo.setObjectName("filterCombo")
            self.school_combo.setMinimumWidth(200)
            filters_layout.addWidget(self.school_combo)
            
            # اختيار الطالب
            student_label = QLabel("الطالب:")
            student_label.setObjectName("filterLabel")
            filters_layout.addWidget(student_label)
            
            self.student_combo = QComboBox()
            self.student_combo.setObjectName("filterCombo")
            self.student_combo.setMinimumWidth(200)
            filters_layout.addWidget(self.student_combo)
            
            # فلتر الحالة
            status_label = QLabel("حالة القسط:")
            status_label.setObjectName("filterLabel")
            filters_layout.addWidget(status_label)
            
            self.status_combo = QComboBox()
            self.status_combo.setObjectName("filterCombo")
            self.status_combo.addItems(["جميع الأقساط", "مدفوع", "مستحق", "متأخر", "ملغي"])
            filters_layout.addWidget(self.status_combo)
            
            filters_layout.addStretch()
            
            toolbar_layout.addLayout(filters_layout)
            
            # الصف الثاني - فلاتر التاريخ والعمليات
            actions_layout = QHBoxLayout()
            
            # فلتر تاريخ الاستحقاق
            due_date_label = QLabel("تاريخ الاستحقاق من:")
            due_date_label.setObjectName("filterLabel")
            actions_layout.addWidget(due_date_label)
            
            self.due_date_from = QDateEdit()
            self.due_date_from.setObjectName("dateInput")
            self.due_date_from.setDate(QDate.currentDate().addDays(-30))
            self.due_date_from.setCalendarPopup(True)
            actions_layout.addWidget(self.due_date_from)
            
            to_label = QLabel("إلى:")
            to_label.setObjectName("filterLabel")
            actions_layout.addWidget(to_label)
            
            self.due_date_to = QDateEdit()
            self.due_date_to.setObjectName("dateInput")
            self.due_date_to.setDate(QDate.currentDate().addDays(30))
            self.due_date_to.setCalendarPopup(True)
            actions_layout.addWidget(self.due_date_to)
            
            actions_layout.addStretch()
            
            # أزرار العمليات
            self.add_installment_button = QPushButton("إضافة قسط")
            self.add_installment_button.setObjectName("primaryButton")
            actions_layout.addWidget(self.add_installment_button)
            
            self.record_payment_button = QPushButton("تسجيل دفع")
            self.record_payment_button.setObjectName("successButton")
            actions_layout.addWidget(self.record_payment_button)
            
            self.generate_report_button = QPushButton("تقرير مالي")
            self.generate_report_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.generate_report_button)
            
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("refreshButton")
            actions_layout.addWidget(self.refresh_button)
            
            toolbar_layout.addLayout(actions_layout)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise
    
    def create_installments_table(self, layout):
        """إنشاء جدول الأقساط"""
        try:
            # إطار الجدول
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")
            
            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)
            
            # إنشاء الجدول
            self.installments_table = QTableWidget()
            self.installments_table.setObjectName("dataTable")
            
            # إعداد الأعمدة
            columns = [
                "المعرف", "الطالب", "المدرسة", "نوع القسط", "المبلغ",
                "تاريخ الاستحقاق", "تاريخ الدفع", "المبلغ المدفوع", 
                "المتبقي", "الحالة", "ملاحظات"
            ]
            
            self.installments_table.setColumnCount(len(columns))
            self.installments_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.installments_table.setAlternatingRowColors(True)
            self.installments_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.installments_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.installments_table.setSortingEnabled(True)
            self.installments_table.setShowGrid(False)
            
            # تخصيص عرض الأعمدة
            header = self.installments_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setDefaultSectionSize(120)
            header.resizeSection(0, 80)   # المعرف
            header.resizeSection(1, 160)  # الطالب
            header.resizeSection(2, 130)  # المدرسة
            header.resizeSection(3, 120)  # نوع القسط
            header.resizeSection(4, 100)  # المبلغ
            header.resizeSection(5, 110)  # تاريخ الاستحقاق
            header.resizeSection(6, 110)  # تاريخ الدفع
            header.resizeSection(7, 100)  # المبلغ المدفوع
            header.resizeSection(8, 100)  # المتبقي
            header.resizeSection(9, 80)   # الحالة
            
            # إخفاء العمود الأول (المعرف) 
            self.installments_table.setColumnHidden(0, True)
            
            # ربط الأحداث
            self.installments_table.cellDoubleClicked.connect(self.edit_installment)
            self.installments_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.installments_table.customContextMenuRequested.connect(self.show_context_menu)
            
            table_layout.addWidget(self.installments_table)
            layout.addWidget(table_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول الأقساط: {e}")
            raise
    
    def create_financial_summary(self, layout):
        """إنشاء ملخص مالي"""
        try:
            summary_frame = QFrame()
            summary_frame.setObjectName("summaryFrame")
            
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(15, 10, 15, 10)
            
            # ملخص الأرقام
            numbers_layout = QVBoxLayout()
            
            summary_title = QLabel("الملخص المالي")
            summary_title.setObjectName("summaryTitle")
            numbers_layout.addWidget(summary_title)
            
            numbers_grid = QHBoxLayout()
            
            # إجمالي المبالغ
            total_layout = QVBoxLayout()
            self.total_amount_label = QLabel("إجمالي المبالغ")
            self.total_amount_label.setObjectName("summaryLabel")
            total_layout.addWidget(self.total_amount_label)
            
            self.total_amount_value = QLabel("0 د.ع")
            self.total_amount_value.setObjectName("summaryValue")
            total_layout.addWidget(self.total_amount_value)
            numbers_grid.addLayout(total_layout)
            
            # المبالغ المدفوعة
            paid_layout = QVBoxLayout()
            self.paid_label = QLabel("المدفوع")
            self.paid_label.setObjectName("summaryLabel")
            paid_layout.addWidget(self.paid_label)
            
            self.paid_value = QLabel("0 د.ع")
            self.paid_value.setObjectName("summaryValueSuccess")
            paid_layout.addWidget(self.paid_value)
            numbers_grid.addLayout(paid_layout)
            
            # المبالغ المستحقة
            pending_layout = QVBoxLayout()
            self.pending_label = QLabel("المستحق")
            self.pending_label.setObjectName("summaryLabel")
            pending_layout.addWidget(self.pending_label)
            
            self.pending_value = QLabel("0 د.ع")
            self.pending_value.setObjectName("summaryValueWarning")
            pending_layout.addWidget(self.pending_value)
            numbers_grid.addLayout(pending_layout)
            
            # المبالغ المتأخرة
            overdue_layout = QVBoxLayout()
            self.overdue_label = QLabel("متأخر")
            self.overdue_label.setObjectName("summaryLabel")
            overdue_layout.addWidget(self.overdue_label)
            
            self.overdue_value = QLabel("0 د.ع")
            self.overdue_value.setObjectName("summaryValueDanger")
            overdue_layout.addWidget(self.overdue_value)
            numbers_grid.addLayout(overdue_layout)
            
            numbers_layout.addLayout(numbers_grid)
            summary_layout.addLayout(numbers_layout)
            
            # شريط التقدم
            progress_layout = QVBoxLayout()
            
            progress_title = QLabel("معدل التحصيل")
            progress_title.setObjectName("summaryLabel")
            progress_layout.addWidget(progress_title)
            
            self.collection_progress = QProgressBar()
            self.collection_progress.setObjectName("progressBar")
            self.collection_progress.setMinimum(0)
            self.collection_progress.setMaximum(100)
            self.collection_progress.setValue(0)
            self.collection_progress.setFormat("%p%")
            progress_layout.addWidget(self.collection_progress)
            
            self.collection_percentage_label = QLabel("0% من المبلغ الإجمالي")
            self.collection_percentage_label.setObjectName("summaryLabel")
            progress_layout.addWidget(self.collection_percentage_label)
            
            summary_layout.addLayout(progress_layout)
            
            # إحصائيات أخرى
            stats_layout = QVBoxLayout()
            
            self.displayed_count_label = QLabel("عدد الأقساط المعروضة: 0")
            self.displayed_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.displayed_count_label)
            
            self.overdue_count_label = QLabel("الأقساط المتأخرة: 0")
            self.overdue_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.overdue_count_label)
            
            self.due_today_label = QLabel("تستحق اليوم: 0")
            self.due_today_label.setObjectName("statLabel")
            stats_layout.addWidget(self.due_today_label)
            
            summary_layout.addLayout(stats_layout)
            
            layout.addWidget(summary_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الملخص المالي: {e}")
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            # ربط أزرار العمليات
            self.add_installment_button.clicked.connect(self.add_installment)
            self.record_payment_button.clicked.connect(self.record_payment)
            self.generate_report_button.clicked.connect(self.generate_report)
            self.refresh_button.clicked.connect(self.refresh)
            
            # ربط الفلاتر
            self.school_combo.currentTextChanged.connect(self.on_school_changed)
            self.student_combo.currentTextChanged.connect(self.apply_filters)
            self.status_combo.currentTextChanged.connect(self.apply_filters)
            self.due_date_from.dateChanged.connect(self.apply_filters)
            self.due_date_to.dateChanged.connect(self.apply_filters)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
    def load_initial_data(self):
        """تحميل البيانات الأولية"""
        try:
            self.load_schools()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل البيانات الأولية: {e}")
    
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            self.school_combo.clear()
            self.school_combo.addItem("جميع المدارس", None)
            
            # جلب المدارس من قاعدة البيانات
            query = "SELECT id, name_ar FROM schools ORDER BY name_ar"
            schools = db_manager.execute_query(query)
            
            if schools:
                for school in schools:
                    self.school_combo.addItem(school[1], school[0])
            
            # تحميل الطلاب والأقساط بعد تحميل المدارس
            self.load_students()
            self.refresh()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
    
    def load_students(self):
        """تحميل قائمة الطلاب حسب المدرسة المحددة"""
        try:
            self.student_combo.clear()
            self.student_combo.addItem("جميع الطلاب", None)
            
            selected_school_id = self.school_combo.currentData()
            
            # بناء الاستعلام
            if selected_school_id:
                query = """
                    SELECT id, name as full_name
                    FROM students 
                    WHERE school_id = ? AND status = 'نشط'
                    ORDER BY name
                """
                params = [selected_school_id]
            else:
                query = """
                    SELECT id, name as full_name
                    FROM students 
                    WHERE status = 'نشط'
                    ORDER BY name
                """
                params = []
            
            students = db_manager.execute_query(query, params)
            
            if students:
                for student in students:
                    self.student_combo.addItem(student[1], student[0])
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الطلاب: {e}")
    
    def on_school_changed(self):
        """معالج تغيير المدرسة"""
        try:
            self.load_students()
            self.apply_filters()
            
        except Exception as e:
            logging.error(f"خطأ في معالج تغيير المدرسة: {e}")
    
    def load_installments(self):
        """تحميل قائمة الأقساط"""
        try:
            # بناء الاستعلام مع الفلاتر
            query = """
                SELECT i.id, s.name as student_name, sc.name_ar as school_name,
                       i.installment_type, i.amount, i.due_date, i.payment_date,
                       i.paid_amount, (i.amount - COALESCE(i.paid_amount, 0)) as remaining,
                       i.status, i.notes
                FROM installments i
                LEFT JOIN students s ON i.student_id = s.id
                LEFT JOIN schools sc ON s.school_id = sc.id
                WHERE 1=1
            """
            params = []
            
            # فلتر المدرسة
            selected_school_id = self.school_combo.currentData()
            if selected_school_id:
                query += " AND s.school_id = ?"
                params.append(selected_school_id)
            
            # فلتر الطالب
            selected_student_id = self.student_combo.currentData()
            if selected_student_id:
                query += " AND i.student_id = ?"
                params.append(selected_student_id)
            
            # فلتر الحالة
            selected_status = self.status_combo.currentText()
            if selected_status and selected_status != "جميع الأقساط":
                query += " AND i.status = ?"
                params.append(selected_status)
            
            # فلتر تاريخ الاستحقاق
            due_from = self.due_date_from.date().toString("yyyy-MM-dd")
            due_to = self.due_date_to.date().toString("yyyy-MM-dd")
            query += " AND i.due_date BETWEEN ? AND ?"
            params.extend([due_from, due_to])
            
            query += " ORDER BY i.due_date DESC, i.created_at DESC"
            
            # تنفيذ الاستعلام
            installments = db_manager.execute_query(query, params)
            
            self.current_installments = installments or []
            self.populate_installments_table()
            self.update_financial_summary()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الأقساط: {e}")
            self.show_error_message("خطأ في التحميل", f"حدث خطأ في تحميل بيانات الأقساط: {str(e)}")
    
    def populate_installments_table(self):
        """ملء جدول الأقساط"""
        try:
            self.installments_table.setRowCount(len(self.current_installments))
            
            for row, installment in enumerate(self.current_installments):
                # المعرف (مخفي)
                self.installments_table.setItem(row, 0, QTableWidgetItem(str(installment[0])))
                
                # الطالب
                self.installments_table.setItem(row, 1, QTableWidgetItem(installment[1] or ""))
                
                # المدرسة
                self.installments_table.setItem(row, 2, QTableWidgetItem(installment[2] or ""))
                
                # نوع القسط
                self.installments_table.setItem(row, 3, QTableWidgetItem(installment[3] or ""))
                
                # المبلغ
                amount = installment[4] or 0
                self.installments_table.setItem(row, 4, QTableWidgetItem(f"{amount:,.0f}"))
                
                # تاريخ الاستحقاق
                due_date = installment[5]
                if due_date:
                    try:
                        date_obj = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                    except:
                        formatted_date = str(due_date)[:10]
                else:
                    formatted_date = ""
                self.installments_table.setItem(row, 5, QTableWidgetItem(formatted_date))
                
                # تاريخ الدفع
                payment_date = installment[6]
                if payment_date:
                    try:
                        date_obj = datetime.fromisoformat(payment_date.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                    except:
                        formatted_date = str(payment_date)[:10]
                else:
                    formatted_date = ""
                self.installments_table.setItem(row, 6, QTableWidgetItem(formatted_date))
                
                # المبلغ المدفوع
                paid_amount = installment[7] or 0
                self.installments_table.setItem(row, 7, QTableWidgetItem(f"{paid_amount:,.0f}"))
                
                # المتبقي
                remaining = installment[8] or 0
                self.installments_table.setItem(row, 8, QTableWidgetItem(f"{remaining:,.0f}"))
                
                # الحالة
                status = installment[9] or "مستحق"
                status_item = QTableWidgetItem(status)
                
                if status == "مدفوع":
                    status_item.setBackground(Qt.green)
                elif status == "متأخر":
                    status_item.setBackground(Qt.red)
                elif status == "مستحق":
                    status_item.setBackground(Qt.yellow)
                elif status == "ملغي":
                    status_item.setBackground(Qt.gray)
                
                self.installments_table.setItem(row, 9, status_item)
                
                # الملاحظات
                notes = installment[10] or ""
                self.installments_table.setItem(row, 10, QTableWidgetItem(notes))
            
            # تحديث إحصائية العدد المعروض
            self.displayed_count_label.setText(f"عدد الأقساط المعروضة: {len(self.current_installments)}")
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الأقساط: {e}")
    
    def update_financial_summary(self):
        """تحديث الملخص المالي"""
        try:
            # حساب الإجماليات للأقساط المعروضة
            total_amount = 0
            paid_amount = 0
            pending_amount = 0
            overdue_amount = 0
            overdue_count = 0
            due_today_count = 0
            
            today = date.today()
            
            for installment in self.current_installments:
                amount = installment[4] or 0
                paid = installment[7] or 0
                remaining = installment[8] or 0
                status = installment[9] or "مستحق"
                due_date_str = installment[5]
                
                total_amount += amount
                paid_amount += paid
                
                if status == "مستحق":
                    pending_amount += remaining
                elif status == "متأخر":
                    overdue_amount += remaining
                    overdue_count += 1
                
                # التحقق من الأقساط المستحقة اليوم
                if due_date_str:
                    try:
                        due_date = datetime.fromisoformat(due_date_str.replace('Z', '+00:00')).date()
                        if due_date == today and status in ["مستحق", "متأخر"]:
                            due_today_count += 1
                    except:
                        pass
            
            # تحديث الملصقات
            self.total_amount_value.setText(f"{total_amount:,.0f} د.ع")
            self.paid_value.setText(f"{paid_amount:,.0f} د.ع")
            self.pending_value.setText(f"{pending_amount:,.0f} د.ع")
            self.overdue_value.setText(f"{overdue_amount:,.0f} د.ع")
            
            # تحديث ملصقات الرأس
            self.total_installments_label.setText(f"إجمالي الأقساط: {len(self.current_installments)}")
            self.paid_amount_label.setText(f"المدفوع: {paid_amount:,.0f} د.ع")
            self.pending_amount_label.setText(f"المستحق: {pending_amount + overdue_amount:,.0f} د.ع")
            
            # حساب معدل التحصيل
            if total_amount > 0:
                collection_rate = (paid_amount / total_amount) * 100
                self.collection_progress.setValue(int(collection_rate))
                self.collection_percentage_label.setText(f"{collection_rate:.1f}% من المبلغ الإجمالي")
            else:
                self.collection_progress.setValue(0)
                self.collection_percentage_label.setText("0% من المبلغ الإجمالي")
            
            # تحديث الإحصائيات الأخرى
            self.overdue_count_label.setText(f"الأقساط المتأخرة: {overdue_count}")
            self.due_today_label.setText(f"تستحق اليوم: {due_today_count}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الملخص المالي: {e}")
    
    def apply_filters(self):
        """تطبيق الفلاتر وإعادة تحميل البيانات"""
        try:
            self.load_installments()
            
        except Exception as e:
            logging.error(f"خطأ في تطبيق الفلاتر: {e}")
    
    def refresh(self):
        """تحديث البيانات"""
        try:
            log_user_action("تحديث صفحة الأقساط")
            self.load_installments()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث صفحة الأقساط: {e}")
    
    def show_context_menu(self, position):
        """عرض قائمة السياق للجدول"""
        try:
            if self.installments_table.itemAt(position):
                menu = QMenu()
                
                edit_action = QAction("تعديل القسط", self)
                edit_action.triggered.connect(lambda: self.edit_selected_installment())
                menu.addAction(edit_action)
                
                payment_action = QAction("تسجيل دفع", self)
                payment_action.triggered.connect(lambda: self.record_payment_for_selected())
                menu.addAction(payment_action)
                
                menu.addSeparator()
                
                cancel_action = QAction("إلغاء القسط", self)
                cancel_action.triggered.connect(lambda: self.cancel_installment())
                menu.addAction(cancel_action)
                
                delete_action = QAction("حذف القسط", self)
                delete_action.triggered.connect(lambda: self.delete_selected_installment())
                menu.addAction(delete_action)
                
                menu.exec_(self.installments_table.mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"خطأ في عرض قائمة السياق: {e}")
    
    def add_installment(self):
        """إضافة قسط جديد"""
        try:
            dialog = AddInstallmentDialog(self)
            dialog.installment_added.connect(self.refresh_installments_table)
            dialog.exec_()
            log_user_action("طلب إضافة قسط جديد")
            
        except Exception as e:
            logging.error(f"خطأ في إضافة قسط: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إضافة القسط:\n{str(e)}")
    
    def edit_installment(self, row, column):
        """تعديل قسط عند الضغط المزدوج"""
        try:
            if row >= 0:
                installment_id = int(self.installments_table.item(row, 0).text())
                self.edit_installment_by_id(installment_id)
                
        except Exception as e:
            logging.error(f"خطأ في تعديل القسط: {e}")
    
    def edit_selected_installment(self):
        """تعديل القسط المحدد"""
        try:
            current_row = self.installments_table.currentRow()
            if current_row >= 0:
                installment_id = int(self.installments_table.item(current_row, 0).text())
                self.edit_installment_by_id(installment_id)
            
        except Exception as e:
            logging.error(f"خطأ في تعديل القسط المحدد: {e}")
    
    def edit_installment_by_id(self, installment_id: int):
        """تعديل قسط بالمعرف"""
        try:
            self.show_info_message("قيد التطوير", f"نافذة تعديل القسط {installment_id} قيد التطوير")
            log_user_action("طلب تعديل قسط", f"المعرف: {installment_id}")
            
        except Exception as e:
            logging.error(f"خطأ في تعديل القسط {installment_id}: {e}")
    
    def record_payment(self):
        """تسجيل دفع عام"""
        try:
            self.show_info_message("قيد التطوير", "نافذة تسجيل الدفع قيد التطوير")
            log_user_action("طلب تسجيل دفع")
            
        except Exception as e:
            logging.error(f"خطأ في تسجيل الدفع: {e}")
    
    def record_payment_for_selected(self):
        """تسجيل دفع للقسط المحدد"""
        try:
            current_row = self.installments_table.currentRow()
            if current_row >= 0:
                installment_id = int(self.installments_table.item(current_row, 0).text())
                self.show_info_message("قيد التطوير", f"نافذة تسجيل دفع للقسط {installment_id} قيد التطوير")
                log_user_action("طلب تسجيل دفع لقسط محدد", f"المعرف: {installment_id}")
            
        except Exception as e:
            logging.error(f"خطأ في تسجيل دفع للقسط المحدد: {e}")
    
    def cancel_installment(self):
        """إلغاء القسط"""
        try:
            current_row = self.installments_table.currentRow()
            if current_row >= 0:
                installment_id = int(self.installments_table.item(current_row, 0).text())
                student_name = self.installments_table.item(current_row, 1).text()
                
                reply = QMessageBox.question(
                    self,
                    "تأكيد الإلغاء",
                    f"هل تريد إلغاء القسط للطالب '{student_name}'؟",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    update_query = "UPDATE installments SET status = 'ملغي' WHERE id = ?"
                    success = db_manager.execute_query(update_query, (installment_id,))
                    
                    if success:
                        log_database_operation("تحديث", "installments", f"إلغاء قسط للطالب {student_name}")
                        log_user_action("إلغاء قسط", f"{student_name}")
                        self.refresh()
                        self.show_info_message("تم الإلغاء", "تم إلغاء القسط بنجاح")
                    else:
                        self.show_error_message("خطأ", "فشل في إلغاء القسط")
            
        except Exception as e:
            logging.error(f"خطأ في إلغاء القسط: {e}")
            self.show_error_message("خطأ", f"حدث خطأ في إلغاء القسط: {str(e)}")
    
    def delete_selected_installment(self):
        """حذف القسط المحدد"""
        try:
            current_row = self.installments_table.currentRow()
            if current_row >= 0:
                installment_id = int(self.installments_table.item(current_row, 0).text())
                student_name = self.installments_table.item(current_row, 1).text()
                
                reply = QMessageBox.question(
                    self,
                    "تأكيد الحذف",
                    f"هل تريد حذف القسط للطالب '{student_name}' نهائياً؟\n\nتحذير: هذا الإجراء لا يمكن التراجع عنه!",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    delete_query = "DELETE FROM installments WHERE id = ?"
                    success = db_manager.execute_query(delete_query, (installment_id,))
                    
                    if success:
                        log_database_operation("حذف", "installments", f"حذف قسط للطالب: {student_name}")
                        log_user_action("حذف قسط", student_name)
                        self.refresh()
                        self.show_info_message("تم الحذف", "تم حذف القسط بنجاح")
                    else:
                        self.show_error_message("خطأ", "فشل في حذف القسط")
            
        except Exception as e:
            logging.error(f"خطأ في حذف القسط: {e}")
            self.show_error_message("خطأ", f"حدث خطأ في حذف القسط: {str(e)}")
    
    def generate_report(self):
        """إنتاج تقرير مالي"""
        try:
            self.show_info_message("قيد التطوير", "ميزة التقارير المالية قيد التطوير")
            log_user_action("طلب إنتاج تقرير مالي")
            
        except Exception as e:
            logging.error(f"خطأ في إنتاج التقرير: {e}")
    
    def show_info_message(self, title: str, message: str):
        """عرض رسالة معلومات"""
        try:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Information)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة المعلومات: {e}")
    
    def show_error_message(self, title: str, message: str):
        """عرض رسالة خطأ"""
        try:
            msg_box = QMessageBox(self)
            msg_box.setIcon(QMessageBox.Critical)
            msg_box.setWindowTitle(title)
            msg_box.setText(message)
            msg_box.setStandardButtons(QMessageBox.Ok)
            msg_box.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة الخطأ: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات الصفحة"""
        try:
            style = """
                /* الإطار الرئيسي */
                QWidget {
                    background-color: #F8F9FA;
                    font-family: 'Segoe UI', Tahoma, Arial;
                    font-size: 12px;
                }
                
                /* رأس الصفحة */
                #headerFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                        stop:0 #E74C3C, stop:1 #C0392B);
                    border-radius: 10px;
                    color: white;
                    margin-bottom: 10px;
                }
                
                #pageTitle {
                    font-size: 24px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 5px;
                }
                
                #pageDesc {
                    font-size: 14px;
                    color: #FADBD8;
                }
                
                #quickStat {
                    font-size: 13px;
                    font-weight: bold;
                    color: white;
                    background-color: rgba(255, 255, 255, 0.2);
                    padding: 5px 10px;
                    border-radius: 15px;
                    margin: 0 5px;
                }
                
                /* شريط الأدوات */
                #toolbarFrame {
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 8px;
                    margin-bottom: 10px;
                }
                
                #filterLabel {
                    font-weight: bold;
                    color: #2C3E50;
                    margin-right: 5px;
                }
                
                #filterCombo, #dateInput {
                    padding: 6px 10px;
                    border: 1px solid #BDC3C7;
                    border-radius: 4px;
                    background-color: white;
                    min-width: 100px;
                }
                
                #filterCombo:focus, #dateInput:focus {
                    border-color: #E74C3C;
                    outline: none;
                }
                
                /* الأزرار */
                #primaryButton {
                    background-color: #E74C3C;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                }
                
                #primaryButton:hover {
                    background-color: #C0392B;
                }
                
                #successButton {
                    background-color: #27AE60;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                }
                
                #successButton:hover {
                    background-color: #229954;
                }
                
                #secondaryButton {
                    background-color: #3498DB;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                }
                
                #secondaryButton:hover {
                    background-color: #2980B9;
                }
                
                #refreshButton {
                    background-color: #95A5A6;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                
                #refreshButton:hover {
                    background-color: #7F8C8D;
                }
                
                /* إطار الجدول */
                #tableFrame {
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 8px;
                }
                
                /* الجدول */
                #dataTable {
                    background-color: white;
                    border: none;
                    border-radius: 6px;
                    gridline-color: #E9ECEF;
                }
                
                #dataTable::item {
                    padding: 8px;
                    border-bottom: 1px solid #F1F2F6;
                }
                
                #dataTable::item:selected {
                    background-color: #FADBD8;
                    color: #C0392B;
                }
                
                #dataTable::item:alternate {
                    background-color: #FAFAFA;
                }
                
                QHeaderView::section {
                    background-color: #34495E;
                    color: white;
                    padding: 10px 8px;
                    border: none;
                    font-weight: bold;
                    font-size: 12px;
                }
                
                QHeaderView::section:hover {
                    background-color: #2C3E50;
                }
                
                /* إطار الملخص المالي */
                #summaryFrame {
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 8px;
                    margin-top: 10px;
                }
                
                #summaryTitle {
                    font-size: 16px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin-bottom: 10px;
                }
                
                #summaryLabel {
                    font-size: 12px;
                    font-weight: bold;
                    color: #7F8C8D;
                    text-align: center;
                }
                
                #summaryValue {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    text-align: center;
                }
                
                #summaryValueSuccess {
                    font-size: 18px;
                    font-weight: bold;
                    color: #27AE60;
                    text-align: center;
                }
                
                #summaryValueWarning {
                    font-size: 18px;
                    font-weight: bold;
                    color: #F39C12;
                    text-align: center;
                }
                
                #summaryValueDanger {
                    font-size: 18px;
                    font-weight: bold;
                    color: #E74C3C;
                    text-align: center;
                }
                
                #statLabel {
                    font-size: 12px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin: 2px 0;
                }
                
                /* شريط التقدم */
                #progressBar {
                    border: 2px solid #BDC3C7;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                    color: white;
                }
                
                #progressBar::chunk {
                    background-color: #27AE60;
                    border-radius: 6px;
                }
                
                /* أشرطة التمرير */
                QScrollBar:vertical {
                    background-color: #F1F2F6;
                    width: 12px;
                    border-radius: 6px;
                }
                
                QScrollBar::handle:vertical {
                    background-color: #BDC3C7;
                    border-radius: 6px;
                    min-height: 20px;
                }
                
                QScrollBar::handle:vertical:hover {
                    background-color: #95A5A6;
                }
                
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                    border: none;
                    background: none;
                }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد تنسيقات صفحة الأقساط: {e}")
