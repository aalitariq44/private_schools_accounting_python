#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة الرسوم الإضافية
"""

import logging
import json
from datetime import datetime, date
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QDateEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QTextEdit, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation

# استيراد نافذة إضافة الرسم الإضافي
from .add_additional_fee_dialog import AddAdditionalFeeDialog


class AdditionalFeesPage(QWidget):
    """صفحة إدارة الرسوم الإضافية"""
    
    # إشارات النافذة
    page_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_fees = []
        self.selected_school_id = None
        self.selected_student_id = None
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        self.load_initial_data()
        
        log_user_action("فتح صفحة إدارة الرسوم الإضافية")
    
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
            
            # جدول الرسوم الإضافية
            self.create_fees_table(layout)
            
            # إحصائيات وملخص
            self.create_summary(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة الرسوم الإضافية: {e}")
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
            
            title_label = QLabel("إدارة الرسوم الإضافية")
            title_label.setObjectName("pageTitle")
            text_layout.addWidget(title_label)
            
            desc_label = QLabel("إدارة الرسوم الإضافية مثل الكتب والنشاطات والخدمات الأخرى")
            desc_label.setObjectName("pageDesc")
            text_layout.addWidget(desc_label)
            
            header_layout.addLayout(text_layout)
            header_layout.addStretch()
            
            # إحصائيات سريعة في الرأس
            stats_layout = QHBoxLayout()
            
            self.total_fees_label = QLabel("إجمالي الرسوم: 0")
            self.total_fees_label.setObjectName("quickStat")
            stats_layout.addWidget(self.total_fees_label)
            
            self.collected_amount_label = QLabel("المحصل: 0 د.ع")
            self.collected_amount_label.setObjectName("quickStat")
            stats_layout.addWidget(self.collected_amount_label)
            
            self.pending_fees_label = QLabel("المستحق: 0 د.ع")
            self.pending_fees_label.setObjectName("quickStat")
            stats_layout.addWidget(self.pending_fees_label)
            
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
            
            # نوع الرسم
            fee_type_label = QLabel("نوع الرسم:")
            fee_type_label.setObjectName("filterLabel")
            filters_layout.addWidget(fee_type_label)
            
            self.fee_type_combo = QComboBox()
            self.fee_type_combo.setObjectName("filterCombo")
            self.fee_type_combo.addItems([
                "جميع الأنواع", "رسوم كتب", "رسوم نشاطات", "رسوم نقل", 
                "رسوم امتحانات", "رسوم شهادات", "رسوم أخرى"
            ])
            filters_layout.addWidget(self.fee_type_combo)
            
            # فلتر الحالة
            status_label = QLabel("حالة الرسم:")
            status_label.setObjectName("filterLabel")
            filters_layout.addWidget(status_label)
            
            self.status_combo = QComboBox()
            self.status_combo.setObjectName("filterCombo")
            self.status_combo.addItems(["جميع الرسوم", "مدفوع", "مستحق", "ملغي"])
            filters_layout.addWidget(self.status_combo)
            
            filters_layout.addStretch()
            
            toolbar_layout.addLayout(filters_layout)
            
            # الصف الثاني - البحث والعمليات
            actions_layout = QHBoxLayout()
            
            # البحث
            search_label = QLabel("البحث:")
            search_label.setObjectName("filterLabel")
            actions_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setObjectName("searchInput")
            self.search_input.setPlaceholderText("ابحث في الرسوم بالوصف أو اسم الطالب...")
            self.search_input.setMinimumWidth(300)
            actions_layout.addWidget(self.search_input)
            
            actions_layout.addStretch()
            
            # أزرار العمليات
            self.add_fee_button = QPushButton("إضافة رسم")
            self.add_fee_button.setObjectName("primaryButton")
            actions_layout.addWidget(self.add_fee_button)
            
            self.collect_fee_button = QPushButton("تحصيل رسم")
            self.collect_fee_button.setObjectName("successButton")
            actions_layout.addWidget(self.collect_fee_button)
            
            self.bulk_add_button = QPushButton("إضافة مجمعة")
            self.bulk_add_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.bulk_add_button)
            
            self.export_fees_button = QPushButton("تصدير التقرير")
            self.export_fees_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.export_fees_button)
            
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("refreshButton")
            actions_layout.addWidget(self.refresh_button)
            
            toolbar_layout.addLayout(actions_layout)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise
    
    def create_fees_table(self, layout):
        """إنشاء جدول الرسوم الإضافية"""
        try:
            # إطار الجدول
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")
            
            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)
            
            # إنشاء الجدول
            self.fees_table = QTableWidget()
            self.fees_table.setObjectName("dataTable")
            
            # إعداد الأعمدة
            columns = [
                "المعرف", "الطالب", "المدرسة", "نوع الرسم", "الوصف",
                "المبلغ", "تاريخ الإضافة", "تاريخ التحصيل", 
                "المبلغ المحصل", "الحالة", "ملاحظات"
            ]
            
            self.fees_table.setColumnCount(len(columns))
            self.fees_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.fees_table.setAlternatingRowColors(True)
            self.fees_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.fees_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.fees_table.setSortingEnabled(True)
            self.fees_table.setShowGrid(False)
            
            # تخصيص عرض الأعمدة
            header = self.fees_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setDefaultSectionSize(120)
            header.resizeSection(0, 80)   # المعرف
            header.resizeSection(1, 160)  # الطالب
            header.resizeSection(2, 130)  # المدرسة
            header.resizeSection(3, 120)  # نوع الرسم
            header.resizeSection(4, 150)  # الوصف
            header.resizeSection(5, 100)  # المبلغ
            header.resizeSection(6, 110)  # تاريخ الإضافة
            header.resizeSection(7, 110)  # تاريخ التحصيل
            header.resizeSection(8, 100)  # المبلغ المحصل
            header.resizeSection(9, 80)   # الحالة
            
            # إخفاء العمود الأول (المعرف) 
            self.fees_table.setColumnHidden(0, True)
            
            # ربط الأحداث
            self.fees_table.cellDoubleClicked.connect(self.edit_fee)
            self.fees_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.fees_table.customContextMenuRequested.connect(self.show_context_menu)
            
            table_layout.addWidget(self.fees_table)
            layout.addWidget(table_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول الرسوم الإضافية: {e}")
            raise
    
    def create_summary(self, layout):
        """إنشاء ملخص الرسوم"""
        try:
            summary_frame = QFrame()
            summary_frame.setObjectName("summaryFrame")
            
            summary_layout = QHBoxLayout(summary_frame)
            summary_layout.setContentsMargins(15, 10, 15, 10)
            
            # ملخص الأرقام
            numbers_layout = QVBoxLayout()
            
            summary_title = QLabel("ملخص الرسوم الإضافية")
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
            
            # المبالغ المحصلة
            collected_layout = QVBoxLayout()
            self.collected_label = QLabel("المحصل")
            self.collected_label.setObjectName("summaryLabel")
            collected_layout.addWidget(self.collected_label)
            
            self.collected_value = QLabel("0 د.ع")
            self.collected_value.setObjectName("summaryValueSuccess")
            collected_layout.addWidget(self.collected_value)
            numbers_grid.addLayout(collected_layout)
            
            # المبالغ المستحقة
            pending_layout = QVBoxLayout()
            self.pending_summary_label = QLabel("المستحق")
            self.pending_summary_label.setObjectName("summaryLabel")
            pending_layout.addWidget(self.pending_summary_label)
            
            self.pending_summary_value = QLabel("0 د.ع")
            self.pending_summary_value.setObjectName("summaryValueWarning")
            pending_layout.addWidget(self.pending_summary_value)
            numbers_grid.addLayout(pending_layout)
            
            numbers_layout.addLayout(numbers_grid)
            summary_layout.addLayout(numbers_layout)
            
            # إحصائيات حسب النوع
            types_layout = QVBoxLayout()
            
            types_title = QLabel("إحصائيات حسب النوع")
            types_title.setObjectName("summaryLabel")
            types_layout.addWidget(types_title)
            
            self.books_fees_label = QLabel("رسوم كتب: 0 د.ع")
            self.books_fees_label.setObjectName("statLabel")
            types_layout.addWidget(self.books_fees_label)
            
            self.activities_fees_label = QLabel("رسوم نشاطات: 0 د.ع")
            self.activities_fees_label.setObjectName("statLabel")
            types_layout.addWidget(self.activities_fees_label)
            
            self.transport_fees_label = QLabel("رسوم نقل: 0 د.ع")
            self.transport_fees_label.setObjectName("statLabel")
            types_layout.addWidget(self.transport_fees_label)
            
            self.other_fees_label = QLabel("رسوم أخرى: 0 د.ع")
            self.other_fees_label.setObjectName("statLabel")
            types_layout.addWidget(self.other_fees_label)
            
            summary_layout.addLayout(types_layout)
            
            # إحصائيات أخرى
            stats_layout = QVBoxLayout()
            
            self.displayed_count_label = QLabel("عدد الرسوم المعروضة: 0")
            self.displayed_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.displayed_count_label)
            
            self.pending_count_label = QLabel("الرسوم المستحقة: 0")
            self.pending_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.pending_count_label)
            
            self.collected_count_label = QLabel("الرسوم المحصلة: 0")
            self.collected_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.collected_count_label)
            
            summary_layout.addLayout(stats_layout)
            
            layout.addWidget(summary_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء ملخص الرسوم: {e}")
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            # ربط أزرار العمليات
            self.add_fee_button.clicked.connect(self.add_fee)
            self.collect_fee_button.clicked.connect(self.collect_fee)
            self.bulk_add_button.clicked.connect(self.bulk_add_fees)
            self.export_fees_button.clicked.connect(self.export_fees)
            self.refresh_button.clicked.connect(self.refresh)
            
            # ربط الفلاتر
            self.school_combo.currentTextChanged.connect(self.on_school_changed)
            self.student_combo.currentTextChanged.connect(self.apply_filters)
            self.fee_type_combo.currentTextChanged.connect(self.apply_filters)
            self.status_combo.currentTextChanged.connect(self.apply_filters)
            self.search_input.textChanged.connect(self.apply_filters)
            
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
            schools = db_manager.execute_query(query, fetch_all=True)
            
            if schools:
                for school in schools:
                    self.school_combo.addItem(school[1], school[0])
            
            # تحميل الطلاب والرسوم بعد تحميل المدارس
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
                    SELECT id, full_name 
                    FROM students 
                    WHERE school_id = ? AND status = 'نشط'
                    ORDER BY full_name
                """
                params = [selected_school_id]
            else:
                query = """
                    SELECT id, full_name 
                    FROM students 
                    WHERE status = 'نشط'
                    ORDER BY full_name
                """
                params = []
            
            students = db_manager.execute_query(query, params, fetch_all=True)
            
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
    
    def load_fees(self):
        """تحميل قائمة الرسوم الإضافية"""
        try:
            # بناء الاستعلام مع الفلاتر
            query = """
                SELECT af.id, s.full_name as student_name, sc.name_ar as school_name,
                       af.fee_type, af.description, af.amount, af.created_at,
                       af.collection_date, af.collected_amount, af.status, af.notes
                FROM additional_fees af
                LEFT JOIN students s ON af.student_id = s.id
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
                query += " AND af.student_id = ?"
                params.append(selected_student_id)
            
            # فلتر نوع الرسم
            selected_fee_type = self.fee_type_combo.currentText()
            if selected_fee_type and selected_fee_type != "جميع الأنواع":
                query += " AND af.fee_type = ?"
                params.append(selected_fee_type)
            
            # فلتر الحالة
            selected_status = self.status_combo.currentText()
            if selected_status and selected_status != "جميع الرسوم":
                query += " AND af.status = ?"
                params.append(selected_status)
            
            # فلتر البحث
            search_text = self.search_input.text().strip()
            if search_text:
                query += " AND (af.description LIKE ? OR s.full_name LIKE ?)"
                search_param = f"%{search_text}%"
                params.extend([search_param, search_param])
            
            query += " ORDER BY af.created_at DESC"
            
            # تنفيذ الاستعلام
            fees = db_manager.execute_query(query, params, fetch_all=True)
            
            self.current_fees = fees or []
            self.populate_fees_table()
            self.update_summary()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الرسوم الإضافية: {e}")
            self.show_error_message("خطأ في التحميل", f"حدث خطأ في تحميل بيانات الرسوم الإضافية: {str(e)}")
    
    def populate_fees_table(self):
        """ملء جدول الرسوم الإضافية"""
        try:
            self.fees_table.setRowCount(len(self.current_fees))
            
            for row, fee in enumerate(self.current_fees):
                # المعرف (مخفي)
                self.fees_table.setItem(row, 0, QTableWidgetItem(str(fee[0])))
                
                # الطالب
                self.fees_table.setItem(row, 1, QTableWidgetItem(fee[1] or ""))
                
                # المدرسة
                self.fees_table.setItem(row, 2, QTableWidgetItem(fee[2] or ""))
                
                # نوع الرسم
                self.fees_table.setItem(row, 3, QTableWidgetItem(fee[3] or ""))
                
                # الوصف
                self.fees_table.setItem(row, 4, QTableWidgetItem(fee[4] or ""))
                
                # المبلغ
                amount = fee[5] or 0
                self.fees_table.setItem(row, 5, QTableWidgetItem(f"{amount:,.0f}"))
                
                # تاريخ الإضافة
                created_at = fee[6]
                if created_at:
                    try:
                        date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                    except:
                        formatted_date = str(created_at)[:10]
                else:
                    formatted_date = ""
                self.fees_table.setItem(row, 6, QTableWidgetItem(formatted_date))
                
                # تاريخ التحصيل
                collection_date = fee[7]
                if collection_date:
                    try:
                        date_obj = datetime.fromisoformat(collection_date.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                    except:
                        formatted_date = str(collection_date)[:10]
                else:
                    formatted_date = ""
                self.fees_table.setItem(row, 7, QTableWidgetItem(formatted_date))
                
                # المبلغ المحصل
                collected_amount = fee[8] or 0
                self.fees_table.setItem(row, 8, QTableWidgetItem(f"{collected_amount:,.0f}"))
                
                # الحالة
                status = fee[9] or "مستحق"
                status_item = QTableWidgetItem(status)
                
                if status == "مدفوع":
                    status_item.setBackground(Qt.green)
                elif status == "مستحق":
                    status_item.setBackground(Qt.yellow)
                elif status == "ملغي":
                    status_item.setBackground(Qt.gray)
                
                self.fees_table.setItem(row, 9, status_item)
                
                # الملاحظات
                notes = fee[10] or ""
                self.fees_table.setItem(row, 10, QTableWidgetItem(notes))
            
            # تحديث إحصائية العدد المعروض
            self.displayed_count_label.setText(f"عدد الرسوم المعروضة: {len(self.current_fees)}")
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الرسوم الإضافية: {e}")
    
    def update_summary(self):
        """تحديث ملخص الرسوم"""
        try:
            # حساب الإجماليات للرسوم المعروضة
            total_amount = 0
            collected_amount = 0
            pending_amount = 0
            pending_count = 0
            collected_count = 0
            
            # إحصائيات حسب النوع
            books_amount = 0
            activities_amount = 0
            transport_amount = 0
            other_amount = 0
            
            for fee in self.current_fees:
                amount = fee[5] or 0
                collected = fee[8] or 0
                status = fee[9] or "مستحق"
                fee_type = fee[3] or ""
                
                total_amount += amount
                collected_amount += collected
                
                if status == "مستحق":
                    pending_amount += (amount - collected)
                    pending_count += 1
                elif status == "مدفوع":
                    collected_count += 1
                
                # تصنيف حسب النوع
                if fee_type == "رسوم كتب":
                    books_amount += collected
                elif fee_type == "رسوم نشاطات":
                    activities_amount += collected
                elif fee_type == "رسوم نقل":
                    transport_amount += collected
                else:
                    other_amount += collected
            
            # تحديث الملصقات الرئيسية
            self.total_amount_value.setText(f"{total_amount:,.0f} د.ع")
            self.collected_value.setText(f"{collected_amount:,.0f} د.ع")
            self.pending_summary_value.setText(f"{pending_amount:,.0f} د.ع")
            
            # تحديث ملصقات الرأس
            self.total_fees_label.setText(f"إجمالي الرسوم: {len(self.current_fees)}")
            self.collected_amount_label.setText(f"المحصل: {collected_amount:,.0f} د.ع")
            self.pending_fees_label.setText(f"المستحق: {pending_amount:,.0f} د.ع")
            
            # تحديث الإحصائيات حسب النوع
            self.books_fees_label.setText(f"رسوم كتب: {books_amount:,.0f} د.ع")
            self.activities_fees_label.setText(f"رسوم نشاطات: {activities_amount:,.0f} د.ع")
            self.transport_fees_label.setText(f"رسوم نقل: {transport_amount:,.0f} د.ع")
            self.other_fees_label.setText(f"رسوم أخرى: {other_amount:,.0f} د.ع")
            
            # تحديث الإحصائيات الأخرى
            self.pending_count_label.setText(f"الرسوم المستحقة: {pending_count}")
            self.collected_count_label.setText(f"الرسوم المحصلة: {collected_count}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث ملخص الرسوم: {e}")
    
    def apply_filters(self):
        """تطبيق الفلاتر وإعادة تحميل البيانات"""
        try:
            self.load_fees()
            
        except Exception as e:
            logging.error(f"خطأ في تطبيق الفلاتر: {e}")
    
    def refresh(self):
        """تحديث البيانات"""
        try:
            log_user_action("تحديث صفحة الرسوم الإضافية")
            self.load_fees()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث صفحة الرسوم الإضافية: {e}")
    
    def show_context_menu(self, position):
        """عرض قائمة السياق للجدول"""
        try:
            if self.fees_table.itemAt(position):
                menu = QMenu()
                
                edit_action = QAction("تعديل الرسم", self)
                edit_action.triggered.connect(lambda: self.edit_selected_fee())
                menu.addAction(edit_action)
                
                collect_action = QAction("تحصيل الرسم", self)
                collect_action.triggered.connect(lambda: self.collect_selected_fee())
                menu.addAction(collect_action)
                
                menu.addSeparator()
                
                cancel_action = QAction("إلغاء الرسم", self)
                cancel_action.triggered.connect(lambda: self.cancel_fee())
                menu.addAction(cancel_action)
                
                delete_action = QAction("حذف الرسم", self)
                delete_action.triggered.connect(lambda: self.delete_selected_fee())
                menu.addAction(delete_action)
                
                menu.exec_(self.fees_table.mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"خطأ في عرض قائمة السياق: {e}")
    
    def add_fee(self):
        """إضافة رسم جديد"""
        try:
            dialog = AddAdditionalFeeDialog(self)
            dialog.fee_added.connect(self.refresh_fees_table)
            dialog.exec_()
            log_user_action("طلب إضافة رسم إضافي")
            
        except Exception as e:
            logging.error(f"خطأ في إضافة رسم: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إضافة الرسم:\n{str(e)}")
    
    def edit_fee(self, row, column):
        """تعديل رسم عند الضغط المزدوج"""
        try:
            if row >= 0:
                fee_id = int(self.fees_table.item(row, 0).text())
                self.edit_fee_by_id(fee_id)
                
        except Exception as e:
            logging.error(f"خطأ في تعديل الرسم: {e}")
    
    def edit_selected_fee(self):
        """تعديل الرسم المحدد"""
        try:
            current_row = self.fees_table.currentRow()
            if current_row >= 0:
                fee_id = int(self.fees_table.item(current_row, 0).text())
                self.edit_fee_by_id(fee_id)
            
        except Exception as e:
            logging.error(f"خطأ في تعديل الرسم المحدد: {e}")
    
    def edit_fee_by_id(self, fee_id: int):
        """تعديل رسم بالمعرف"""
        try:
            self.show_info_message("قيد التطوير", f"نافذة تعديل الرسم {fee_id} قيد التطوير")
            log_user_action("طلب تعديل رسم إضافي", f"المعرف: {fee_id}")
            
        except Exception as e:
            logging.error(f"خطأ في تعديل الرسم {fee_id}: {e}")
    
    def collect_fee(self):
        """تحصيل رسم عام"""
        try:
            self.show_info_message("قيد التطوير", "نافذة تحصيل الرسوم قيد التطوير")
            log_user_action("طلب تحصيل رسم")
            
        except Exception as e:
            logging.error(f"خطأ في تحصيل الرسم: {e}")
    
    def collect_selected_fee(self):
        """تحصيل الرسم المحدد"""
        try:
            current_row = self.fees_table.currentRow()
            if current_row >= 0:
                fee_id = int(self.fees_table.item(current_row, 0).text())
                self.show_info_message("قيد التطوير", f"نافذة تحصيل الرسم {fee_id} قيد التطوير")
                log_user_action("طلب تحصيل رسم محدد", f"المعرف: {fee_id}")
            
        except Exception as e:
            logging.error(f"خطأ في تحصيل الرسم المحدد: {e}")
    
    def cancel_fee(self):
        """إلغاء الرسم"""
        try:
            current_row = self.fees_table.currentRow()
            if current_row >= 0:
                fee_id = int(self.fees_table.item(current_row, 0).text())
                student_name = self.fees_table.item(current_row, 1).text()
                fee_description = self.fees_table.item(current_row, 4).text()
                
                reply = QMessageBox.question(
                    self,
                    "تأكيد الإلغاء",
                    f"هل تريد إلغاء الرسم '{fee_description}' للطالب '{student_name}'؟",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    update_query = "UPDATE additional_fees SET status = 'ملغي' WHERE id = ?"
                    success = db_manager.execute_query(update_query, (fee_id,))
                    
                    if success:
                        log_database_operation("تحديث", "additional_fees", f"إلغاء رسم {fee_description} للطالب {student_name}")
                        log_user_action("إلغاء رسم إضافي", f"{student_name} - {fee_description}")
                        self.refresh()
                        self.show_info_message("تم الإلغاء", "تم إلغاء الرسم بنجاح")
                    else:
                        self.show_error_message("خطأ", "فشل في إلغاء الرسم")
            
        except Exception as e:
            logging.error(f"خطأ في إلغاء الرسم: {e}")
            self.show_error_message("خطأ", f"حدث خطأ في إلغاء الرسم: {str(e)}")
    
    def delete_selected_fee(self):
        """حذف الرسم المحدد"""
        try:
            current_row = self.fees_table.currentRow()
            if current_row >= 0:
                fee_id = int(self.fees_table.item(current_row, 0).text())
                student_name = self.fees_table.item(current_row, 1).text()
                fee_description = self.fees_table.item(current_row, 4).text()
                
                reply = QMessageBox.question(
                    self,
                    "تأكيد الحذف",
                    f"هل تريد حذف الرسم '{fee_description}' للطالب '{student_name}' نهائياً؟\n\nتحذير: هذا الإجراء لا يمكن التراجع عنه!",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    delete_query = "DELETE FROM additional_fees WHERE id = ?"
                    success = db_manager.execute_query(delete_query, (fee_id,))
                    
                    if success:
                        log_database_operation("حذف", "additional_fees", f"حذف رسم {fee_description} للطالب: {student_name}")
                        log_user_action("حذف رسم إضافي", f"{student_name} - {fee_description}")
                        self.refresh()
                        self.show_info_message("تم الحذف", "تم حذف الرسم بنجاح")
                    else:
                        self.show_error_message("خطأ", "فشل في حذف الرسم")
            
        except Exception as e:
            logging.error(f"خطأ في حذف الرسم: {e}")
            self.show_error_message("خطأ", f"حدث خطأ في حذف الرسم: {str(e)}")
    
    def bulk_add_fees(self):
        """إضافة رسوم مجمعة"""
        try:
            self.show_info_message("قيد التطوير", "ميزة الإضافة المجمعة للرسوم قيد التطوير")
            log_user_action("طلب إضافة رسوم مجمعة")
            
        except Exception as e:
            logging.error(f"خطأ في الإضافة المجمعة: {e}")
    
    def export_fees(self):
        """تصدير تقرير الرسوم"""
        try:
            self.show_info_message("قيد التطوير", "ميزة تصدير تقرير الرسوم قيد التطوير")
            log_user_action("طلب تصدير تقرير الرسوم")
            
        except Exception as e:
            logging.error(f"خطأ في تصدير التقرير: {e}")
    
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
                        stop:0 #9B59B6, stop:1 #8E44AD);
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
                    color: #E8DAEF;
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
                
                #filterCombo {
                    padding: 6px 10px;
                    border: 1px solid #BDC3C7;
                    border-radius: 4px;
                    background-color: white;
                    min-width: 100px;
                }
                
                #filterCombo:focus {
                    border-color: #9B59B6;
                    outline: none;
                }
                
                #searchInput {
                    padding: 8px 12px;
                    border: 2px solid #9B59B6;
                    border-radius: 6px;
                    font-size: 13px;
                    background-color: white;
                }
                
                #searchInput:focus {
                    border-color: #8E44AD;
                    outline: none;
                }
                
                /* الأزرار */
                #primaryButton {
                    background-color: #9B59B6;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                }
                
                #primaryButton:hover {
                    background-color: #8E44AD;
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
                    background-color: #E8DAEF;
                    color: #6C3483;
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
                
                /* إطار الملخص */
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
                
                #statLabel {
                    font-size: 12px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin: 2px 0;
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
            logging.error(f"خطأ في إعداد تنسيقات صفحة الرسوم الإضافية: {e}")
