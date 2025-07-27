#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة الطلاب - محدثة
"""

import logging
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QDateEdit, QSpinBox, QAction, QDialog,
    QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation

# استيراد نظام الطباعة
from core.printing import print_manager, PrintHelper, QuickPrintMixin, apply_print_styles, TemplateType
# Override PrintHelper in case of import issues
from core.printing.print_utils import PrintHelper as _PrintHelper
PrintHelper = _PrintHelper

# استيراد نوافذ إدارة الطلاب
from .add_student_dialog import AddStudentDialog
from .edit_student_dialog import EditStudentDialog


class StudentsPage(QWidget, QuickPrintMixin):
    """صفحة إدارة الطلاب"""
    
    # إشارات النافذة
    page_loaded = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_students = []
        self.selected_school_id = None
        
        self.setup_ui()
        self.setup_styles()
        self.setup_connections()
        # إعداد الطباعة باستخدام QuickPrintMixin
        self.setup_printing(TemplateType.STUDENT_LIST, self.get_current_data_for_print)
        self.load_schools()
        
        log_user_action("فتح صفحة إدارة الطلاب")
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        try:
            # التخطيط الرئيسي
            layout = QVBoxLayout()
            layout.setContentsMargins(20, 20, 20, 20)
            layout.setSpacing(15)
            
            # شريط الأدوات والفلاتر
            self.create_toolbar(layout)
            
            # جدول الطلاب
            self.create_students_table(layout)
            
            # إحصائيات سريعة
            self.create_quick_stats(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة الطلاب: {e}")
            raise
    
    def create_toolbar(self, layout):
        """إنشاء شريط الأدوات والفلاتر"""
        try:
            toolbar_frame = QFrame()
            toolbar_frame.setObjectName("toolbarFrame")
            
            toolbar_layout = QHBoxLayout(toolbar_frame)
            toolbar_layout.setContentsMargins(15, 10, 15, 10)
            
            # فلاتر البحث
            filters_layout = QHBoxLayout()
            
            # فلتر المدرسة
            school_label = QLabel("المدرسة:")
            school_label.setObjectName("filterLabel")
            filters_layout.addWidget(school_label)
            
            self.school_combo = QComboBox()
            self.school_combo.setObjectName("filterCombo")
            filters_layout.addWidget(self.school_combo)
            
            # فلتر الصف
            grade_label = QLabel("الصف:")
            grade_label.setObjectName("filterLabel")
            filters_layout.addWidget(grade_label)
            
            self.grade_combo = QComboBox()
            self.grade_combo.setObjectName("filterCombo")
            self.grade_combo.addItems(["جميع الصفوف", "الأول الابتدائي", "الثاني الابتدائي", 
                                      "الثالث الابتدائي", "الرابع الابتدائي", "الخامس الابتدائي", 
                                      "السادس الابتدائي", "الأول المتوسط", "الثاني المتوسط", 
                                      "الثالث المتوسط", "الرابع العلمي", "الرابع الأدبي",
                                      "الخامس العلمي", "الخامس الأدبي", "السادس العلمي", "السادس الأدبي"])
            filters_layout.addWidget(self.grade_combo)
            
            # فلتر الحالة
            status_label = QLabel("الحالة:")
            status_label.setObjectName("filterLabel")
            filters_layout.addWidget(status_label)
            
            self.status_combo = QComboBox()
            self.status_combo.setObjectName("filterCombo")
            self.status_combo.addItems(["جميع الحالات", "نشط", "منقطع", "متخرج", "محول"])
            filters_layout.addWidget(self.status_combo)
            
            # فلتر الجنس
            gender_label = QLabel("الجنس:")
            gender_label.setObjectName("filterLabel")
            filters_layout.addWidget(gender_label)
            self.gender_combo = QComboBox()
            self.gender_combo.setObjectName("filterCombo")
            self.gender_combo.addItems(["جميع الطلاب", "ذكر", "أنثى"])
            filters_layout.addWidget(self.gender_combo)

            # مربع البحث
            search_label = QLabel("البحث:")
            search_label.setObjectName("filterLabel")
            filters_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setObjectName("searchInput")
            self.search_input.setPlaceholderText("ابحث في أسماء الطلاب...")
            filters_layout.addWidget(self.search_input)
            
            toolbar_layout.addLayout(filters_layout)
            toolbar_layout.addStretch()
            
            # أزرار العمليات
            actions_layout = QHBoxLayout()
            
            self.add_student_button = QPushButton("إضافة طالب")
            self.add_student_button.setObjectName("primaryButton")
            actions_layout.addWidget(self.add_student_button)
            
            # أزرار الطباعة
            self.print_list_button = QPushButton("طباعة القائمة")
            self.print_list_button.setObjectName("printButton")
            actions_layout.addWidget(self.print_list_button)
            
            self.quick_print_button = QPushButton("طباعة سريعة")
            self.quick_print_button.setObjectName("quickPrintButton") 
            actions_layout.addWidget(self.quick_print_button)
            
            self.export_pdf_button = QPushButton("تصدير PDF")
            self.export_pdf_button.setObjectName("exportButton")
            actions_layout.addWidget(self.export_pdf_button)
            
            
            
            toolbar_layout.addLayout(actions_layout)
            
            layout.addWidget(toolbar_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط الأدوات: {e}")
            raise
    
    def create_students_table(self, layout):
        """إنشاء جدول الطلاب"""
        try:
            # إطار الجدول
            table_frame = QFrame()
            table_frame.setObjectName("tableFrame")

            table_layout = QVBoxLayout(table_frame)
            table_layout.setContentsMargins(0, 0, 0, 0)  # إزالة الهوامش تمامًا

            # الجدول
            self.students_table = QTableWidget()
            self.students_table.setObjectName("dataTable")

            # إعداد أعمدة الجدول
            columns = ["المعرف", "الاسم", "المدرسة", "الصف", "الشعبة", "الجنس", "الهاتف", "الحالة", "الرسوم الدراسية", "الإجراءات"]
            self.students_table.setColumnCount(len(columns))
            self.students_table.setHorizontalHeaderLabels(columns)

            # إعداد خصائص الجدول
            self.students_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.students_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.students_table.setAlternatingRowColors(True)
            self.students_table.setSortingEnabled(True)

            # إعداد حجم الأعمدة
            header = self.students_table.horizontalHeader()
            header.setStretchLastSection(True)
            for i in range(len(columns) - 1):
                header.setSectionResizeMode(i, QHeaderView.ResizeToContents)

            # إزالة الحشوات داخل الصفوف
            self.students_table.setStyleSheet("QTableWidget::item { padding: 0px; }")

            # ربط الأحداث
            self.students_table.cellDoubleClicked.connect(self.edit_student)
            self.students_table.setContextMenuPolicy(Qt.CustomContextMenu)
            self.students_table.customContextMenuRequested.connect(self.show_context_menu)

            table_layout.addWidget(self.students_table)
            layout.addWidget(table_frame)

        except Exception as e:
            logging.error(f"خطأ في إنشاء جدول الطلاب: {e}")
            raise
    
    def create_quick_stats(self, layout):
        """إنشاء إحصائيات سريعة"""
        try:
            stats_frame = QFrame()
            stats_frame.setObjectName("statsFrame")
            
            stats_layout = QHBoxLayout(stats_frame)
            stats_layout.setContentsMargins(15, 10, 15, 10)
            
            # عداد الطلاب المعروضين
            self.displayed_count_label = QLabel("عدد الطلاب المعروضين: 0")
            self.displayed_count_label.setObjectName("countLabel")
            stats_layout.addWidget(self.displayed_count_label)

            # إحصائيات إضافية
            self.total_students_label = QLabel("إجمالي الطلاب: 0")
            self.total_students_label.setObjectName("countLabel")
            stats_layout.addWidget(self.total_students_label)

            self.active_students_label = QLabel("الطلاب النشطون: 0")
            self.active_students_label.setObjectName("countLabel")
            stats_layout.addWidget(self.active_students_label)
            
            stats_layout.addStretch()
            
            # معلومات آخر تحديث
            self.last_update_label = QLabel("آخر تحديث: --")
            self.last_update_label.setObjectName("countLabel")
            stats_layout.addWidget(self.last_update_label)

            # زر التحديث
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("refreshButton")
            stats_layout.addWidget(self.refresh_button)
            
            layout.addWidget(stats_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الإحصائيات: {e}")
            raise
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            # ربط أزرار العمليات
            self.add_student_button.clicked.connect(self.add_student)
            self.refresh_button.clicked.connect(self.refresh)
            
            # ربط أزرار الطباعة
            self.print_list_button.clicked.connect(self.print_students_list)
            self.quick_print_button.clicked.connect(self.quick_print_current_data)
            self.export_pdf_button.clicked.connect(self.export_students_pdf)
            
            # ربط الفلاتر
            self.school_combo.currentTextChanged.connect(self.apply_filters)
            self.grade_combo.currentTextChanged.connect(self.apply_filters)
            self.status_combo.currentTextChanged.connect(self.apply_filters)
            self.gender_combo.currentTextChanged.connect(self.apply_filters)
            self.search_input.textChanged.connect(self.apply_filters)
            
        except Exception as e:
            logging.error(f"خطأ في ربط الإشارات: {e}")
    
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
                    self.school_combo.addItem(school['name_ar'], school['id'])
            
            # تحميل الطلاب بعد تحميل المدارس
            self.refresh()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
    
    def load_students(self):
        """تحميل قائمة الطلاب"""
        try:
            # بناء الاستعلام مع الفلاتر
            query = """
                SELECT s.id, s.name, sc.name_ar as school_name,
                       s.grade, s.section, s.gender,
                       s.phone, s.status, s.start_date, s.total_fee
                FROM students s
                LEFT JOIN schools sc ON s.school_id = sc.id
                WHERE 1=1
            """
            params = []
            
            # فلتر المدرسة
            selected_school_id = self.school_combo.currentData()
            if selected_school_id:
                query += " AND s.school_id = ?"
                params.append(selected_school_id)
            
            # فلتر الصف
            selected_grade = self.grade_combo.currentText()
            if selected_grade and selected_grade != "جميع الصفوف":
                query += " AND s.grade = ?"
                params.append(selected_grade)
            
            # فلتر الحالة
            selected_status = self.status_combo.currentText()
            if selected_status and selected_status != "جميع الحالات":
                query += " AND s.status = ?"
                params.append(selected_status)
            
            # فلتر الجنس
            selected_gender = self.gender_combo.currentText()
            if selected_gender and selected_gender != "جميع الطلاب":
                query += " AND s.gender = ?"
                params.append(selected_gender)
            
            # فلتر البحث
            search_text = self.search_input.text().strip()
            if search_text:
                query += " AND s.name LIKE ?"
                params.append(f"%{search_text}%")
            
            query += " ORDER BY s.name"
            
            # تنفيذ الاستعلام
            self.current_students = db_manager.execute_query(query, tuple(params))
            
            # ملء الجدول
            self.fill_students_table()
            
            # تحديث الإحصائيات
            self.update_stats()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الطلاب: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل بيانات الطلاب:\\n{str(e)}")
    
    def fill_students_table(self):
        """ملء جدول الطلاب بالبيانات"""
        try:
            # تنظيف الجدول
            self.students_table.setRowCount(0)
            
            if not self.current_students:
                self.displayed_count_label.setText("عدد الطلاب المعروضين: 0")
                return
            
            # ملء الجدول
            for row_idx, student in enumerate(self.current_students):
                self.students_table.insertRow(row_idx)
                
                # البيانات الأساسية
                items = [
                    str(student['id']),
                    student['name'] or "",
                    student['school_name'] or "",
                    student['grade'] or "",
                    student['section'] or "",
                    student['gender'] or "",
                    student['phone'] or "",
                    student['status'] or "",
                    str(student['total_fee']) if student['total_fee'] else "0"
                ]
                
                for col_idx, item_text in enumerate(items):
                    item = QTableWidgetItem(item_text)
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.students_table.setItem(row_idx, col_idx, item)
                
                # أزرار الإجراءات
                actions_widget = self.create_actions_widget(student['id'])
                self.students_table.setCellWidget(row_idx, 9, actions_widget)
            
            # تحديث العداد
            self.displayed_count_label.setText(f"عدد الطلاب المعروضين: {len(self.current_students)}")
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الطلاب: {e}")
    
    def create_actions_widget(self, student_id):
        """إنشاء ويدجت الإجراءات لكل صف"""
        try:
            widget = QWidget()
            layout = QHBoxLayout(widget)
            layout.setContentsMargins(0, 0, 0, 0)  # إزالة الهوامش لتحسين استخدام المساحة
            layout.setSpacing(10)  # تقليل التباعد بين الأزرار

            # زر التعديل
            edit_btn = QPushButton("تعديل")
            edit_btn.setObjectName("editButton")
            edit_btn.setFixedSize(120, 40)  # ضبط حجم الزر بشكل ثابت
            edit_btn.clicked.connect(lambda: self.edit_student_by_id(student_id))
            layout.addWidget(edit_btn)

            # زر الحذف
            delete_btn = QPushButton("حذف")
            delete_btn.setObjectName("deleteButton")
            delete_btn.setFixedSize(120, 40)  # ضبط حجم الزر بشكل ثابت
            delete_btn.clicked.connect(lambda: self.delete_student(student_id))
            layout.addWidget(delete_btn)

            # زر التفاصيل
            details_btn = QPushButton("تفاصيل")
            details_btn.setObjectName("detailsButton")
            details_btn.setFixedSize(120, 40)  # ضبط حجم الزر بشكل ثابت
            details_btn.clicked.connect(lambda: self.show_student_details(student_id))
            layout.addWidget(details_btn)
            
            # زر طباعة تقرير الطالب
            print_btn = QPushButton("طباعة")
            print_btn.setObjectName("printStudentButton")
            print_btn.setFixedSize(120, 40)
            print_btn.clicked.connect(lambda: self.print_student_report(student_id))
            layout.addWidget(print_btn)

            return widget

        except Exception as e:
            logging.error(f"خطأ في إنشاء ويدجت الإجراءات: {e}")
            return QWidget()
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        try:
            # إحصائيات عامة
            total_query = "SELECT COUNT(*) FROM students"
            total_result = db_manager.execute_query(total_query)
            total_count = total_result[0][0] if total_result else 0
            
            active_query = "SELECT COUNT(*) FROM students WHERE status = 'نشط'"
            active_result = db_manager.execute_query(active_query)
            active_count = active_result[0][0] if active_result else 0
            
            self.total_students_label.setText(f"إجمالي الطلاب: {total_count}")
            self.active_students_label.setText(f"الطلاب النشطون: {active_count}")
            
            # تحديث وقت آخر تحديث
            from datetime import datetime
            self.last_update_label.setText(f"آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الإحصائيات: {e}")
            # تعيين قيم افتراضية في حالة الخطأ
            self.total_students_label.setText("إجمالي الطلاب: --")
            self.active_students_label.setText("الطلاب النشطون: --")
    
    def apply_filters(self):
        """تطبيق الفلاتر وإعادة تحميل البيانات"""
        try:
            self.load_students()
            
        except Exception as e:
            logging.error(f"خطأ في تطبيق الفلاتر: {e}")
    
    def refresh(self):
        """تحديث البيانات"""
        try:
            log_user_action("تحديث صفحة الطلاب")
            self.load_students()
            
        except Exception as e:
            logging.error(f"خطأ في تحديث صفحة الطلاب: {e}")
    
    def show_context_menu(self, position):
        """عرض قائمة السياق للجدول"""
        try:
            if self.students_table.itemAt(position) is None:
                return
            
            menu = QMenu(self)
            
            edit_action = QAction("تعديل", self)
            edit_action.triggered.connect(lambda: self.edit_student(self.students_table.currentRow()))
            menu.addAction(edit_action)
            
            delete_action = QAction("حذف", self)
            delete_action.triggered.connect(lambda: self.delete_student_by_row(self.students_table.currentRow()))
            menu.addAction(delete_action)
            
            menu.exec_(self.students_table.mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"خطأ في عرض قائمة السياق: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات الصفحة"""
        try:
            style = """
                /* الإطار الرئيسي */
                QWidget {
                    background-color: #F8F9FA;
                    font-family: 'Segoe UI', Tahoma, Arial;
                    font-size: 18px;
                }
                
                /* رأس الصفحة */
                #headerFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2=1, 
                        stop:0 #3498DB, stop:1 #2980B9);
                    border-radius: 15px;
                    color: white;
                    margin-bottom: 15px;
                    padding: 20px;
                }
                
                #pageTitle {
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                    margin-bottom: 8px;
                }
                
                #pageDesc {
                    font-size: 18px;
                    color: #E8F4FD;
                }
                
                #quickStat {
                    font-size: 18px;
                    font-weight: bold;
                    color: white;
                    background-color: rgba(255, 255, 255, 0.2);
                    padding: 10px 20px;
                    border-radius: 20px;
                    margin: 0 10px;
                }
                
                /* شريط الأدوات */
                #toolbarFrame {
                    background-color: white;
                    border: 2px solid #E9ECEF;
                    border-radius: 12px;
                    margin-bottom: 15px;
                    padding: 20px;
                }
                
                #filterLabel {
                    font-weight: bold;
                    color: #2C3E50;
                    margin-right: 10px;
                    font-size: 18px;
                }
                
                #filterCombo {
                    padding: 12px 20px;
                    border: 2px solid #BDC3C7;
                    border-radius: 8px;
                    background-color: white;
                    min-width: 150px;
                    font-size: 18px;
                    margin: 5px;
                }
                
                #searchInput {
                    padding: 15px 20px;
                    border: 2px solid #3498DB;
                    border-radius: 10px;
                    font-size: 18px;
                    background-color: white;
                    margin: 5px;
                }
                
                /* الأزرار */
                #primaryButton {
                    background-color: #27AE60;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    min-width: 150px;
                    font-size: 18px;
                    margin: 5px;
                }
                
                #primaryButton:hover {
                    background-color: #229954;
                }
                
                /* أزرار الطباعة */
                #printButton {
                    background-color: #007BFF;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    min-width: 150px;
                    font-size: 18px;
                    margin: 5px;
                }
                
                #printButton:hover {
                    background-color: #0056B3;
                }
                
                #quickPrintButton {
                    background-color: #FFC107;
                    color: #212529;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    min-width: 150px;
                    font-size: 18px;
                    margin: 5px;
                }
                
                #quickPrintButton:hover {
                    background-color: #E0A800;
                }
                
                #exportButton {
                    background-color: #28A745;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    min-width: 150px;
                    font-size: 18px;
                    margin: 5px;
                }
                
                #exportButton:hover {
                    background-color: #1E7E34;
                }
                
                #refreshButton {
                    background-color: #F39C12;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    min-width: 120px;
                    font-size: 18px;
                    margin: 5px;
                }
                
                #refreshButton:hover {
                    background-color: #E67E22;
                }
                
                #editButton, #deleteButton, #detailsButton, #printStudentButton {
                    padding: 8px 15px;
                    border-radius: 5px;
                    font-size: 18px;
                    font-weight: bold;
                    border: none;
                    margin: 2px;
                }
                
                #editButton {
                    background-color: #3498DB;
                    color: white;
                }
                
                #deleteButton {
                    background-color: #E74C3C;
                    color: white;
                }
                
                #detailsButton {
                    background-color: #9B59B6;
                    color: white;
                }
                
                #printStudentButton {
                    background-color: #17A2B8;
                    color: white;
                }
                
                #printStudentButton:hover {
                    background-color: #138496;
                }
                
                /* الجدول */
                QTableWidget {
                    background-color: white;
                    border: 2px solid #E9ECEF;
                    border-radius: 12px;
                    gridline-color: #E9ECEF;
                    font-size: 18px;
                    margin: 10px 0px;
                }
                
                QTableWidget::item {
                    padding: 15px 10px;
                    border-bottom: 1px solid #E9ECEF;
                    font-size: 18px;
                }
                
                QTableWidget::item:selected {
                    background-color: #E3F2FD;
                    color: #1976D2;
                }
                
                QHeaderView::section {
                    background-color: #3498DB;
                    color: white;
                    padding: 15px 10px;
                    font-weight: bold;
                    font-size: 18px;
                    border: none;
                    border-right: 1px solid #2980B9;
                }
                
                /* إحصائيات */
                #statsFrame {
                    background-color: white;
                    border: 2px solid #E9ECEF;
                    border-radius: 12px;
                    margin-top: 15px;
                    padding: 20px;
                }
                
                #countLabel {
                    font-size: 18px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin: 5px;
                }
            """
            
            # إضافة تنسيقات الطباعة
            # style += apply_print_styles()
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد الستايل: {e}")
    
    def add_student(self):
        """إضافة طالب جديد"""
        try:
            dialog = AddStudentDialog(self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh()
                log_user_action("إضافة طالب جديد", "نجح")
                
        except Exception as e:
            logging.error(f"خطأ في إضافة طالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إضافة الطالب:\\n{str(e)}")
    
    def edit_student(self, row):
        """تعديل بيانات طالب"""
        try:
            if row < 0 or row >= self.students_table.rowCount():
                return
            
            # الحصول على ID الطالب من الصف المحدد
            student_id_item = self.students_table.item(row, 0)
            if not student_id_item:
                return
            
            student_id = int(student_id_item.text())
            self.edit_student_by_id(student_id)
                
        except Exception as e:
            logging.error(f"خطأ في تعديل الطالب: {e}")
    
    def edit_student_by_id(self, student_id):
        """تعديل طالب بواسطة المعرف"""
        try:
            dialog = EditStudentDialog(student_id, self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh()
                log_user_action(f"تعديل بيانات الطالب {student_id}", "نجح")
                
        except Exception as e:
            logging.error(f"خطأ في تعديل الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تعديل الطالب:\\n{str(e)}")
    
    def delete_student(self, student_id):
        """حذف طالب"""
        try:
            # تأكيد الحذف
            reply = QMessageBox.question(
                self, "تأكيد الحذف",
                "هل أنت متأكد من حذف هذا الطالب؟\\nسيتم حذف جميع البيانات المرتبطة به.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # حذف الطالب من قاعدة البيانات
                query = "DELETE FROM students WHERE id = ?"
                affected_rows = db_manager.execute_update(query, (student_id,))
                
                if affected_rows > 0:
                    QMessageBox.information(self, "نجح", "تم حذف الطالب بنجاح")
                    self.refresh()
                    log_user_action(f"حذف الطالب {student_id}", "نجح")
                else:
                    QMessageBox.warning(self, "خطأ", "لم يتم العثور على الطالب")
                    
        except Exception as e:
            logging.error(f"خطأ في حذف الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حذف الطالب:\\n{str(e)}")
    
    def delete_student_by_row(self, row):
        """حذف طالب بواسطة رقم الصف"""
        try:
            if row < 0 or row >= self.students_table.rowCount():
                return
            
            student_id_item = self.students_table.item(row, 0)
            if not student_id_item:
                return
            
            student_id = int(student_id_item.text())
            self.delete_student(student_id)
            
        except Exception as e:
            logging.error(f"خطأ في حذف الطالب: {e}")
    
    def show_student_details(self, student_id):
        """عرض صفحة تفاصيل الطالب الشاملة"""
        try:
            from .student_details_page import StudentDetailsPage
            
            # إنشاء صفحة التفاصيل
            details_page = StudentDetailsPage(student_id)
            
            # ربط إشارة الرجوع
            details_page.back_requested.connect(lambda: self.close_details_page(details_page))
            details_page.student_updated.connect(self.refresh)
            
            # الحصول على النافذة الرئيسية وإضافة الصفحة
            main_window = self.get_main_window()
            if main_window:
                # إخفاء الشريط الجانبي مؤقتاً لإعطاء مساحة أكبر
                main_window.show_page_widget(details_page)
            else:
                # عرض في نافذة منفصلة إذا لم نجد النافذة الرئيسية
                dialog = QDialog(self)
                dialog.setWindowTitle(f"تفاصيل الطالب")
                dialog.setModal(True)
                dialog.resize(1200, 800)
                
                layout = QVBoxLayout(dialog)
                layout.setContentsMargins(0, 0, 0, 0)
                layout.addWidget(details_page)
                
                # ربط إشارة الرجوع لإغلاق النافذة
                details_page.back_requested.connect(dialog.accept)
                
                dialog.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض تفاصيل الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"خطأ في عرض تفاصيل الطالب: {str(e)}")
    
    def close_details_page(self, details_page):
        """إغلاق صفحة التفاصيل والعودة لصفحة الطلاب"""
        try:
            main_window = self.get_main_window()
            if main_window:
                main_window.show_students_page()
            
        except Exception as e:
            logging.error(f"خطأ في إغلاق صفحة التفاصيل: {e}")
    
    def get_main_window(self):
        """الحصول على النافذة الرئيسية"""
        try:
            parent = self.parent()
            while parent:
                if hasattr(parent, 'show_page_widget'):
                    return parent
                parent = parent.parent()
            return None
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على النافذة الرئيسية: {e}")
            return None
    
    # وظائف الطباعة الجديدة
    def print_students_list(self):
        """طباعة قائمة الطلاب مع معاينة"""
        try:
            if not self.current_students:
                QMessageBox.warning(self, "تحذير", "لا توجد بيانات للطباعة")
                return
            
            # إعداد بيانات الطلاب للطباعة
            students_data = PrintHelper.format_students_list_for_print(self.current_students)
            
            # إعداد معلومات الفلاتر
            filter_info = self.get_current_filters_info()
            
            # طباعة مع معاينة
            print_manager.print_students_list(students_data, filter_info, self)
            
        except Exception as e:
            logging.error(f"خطأ في طباعة قائمة الطلاب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في الطباعة:\\n{str(e)}")
    
    def print_student_report(self, student_id: int):
        """طباعة تقرير طالب واحد"""
        try:
            # البحث عن بيانات الطالب
            student_data = None
            for student in self.current_students:
                if student['id'] == student_id:
                    student_data = student
                    break
            
            if not student_data:
                # جلب البيانات من قاعدة البيانات
                query = """
                    SELECT s.*, sc.name_ar as school_name
                    FROM students s
                    LEFT JOIN schools sc ON s.school_id = sc.id
                    WHERE s.id = ?
                """
                result = db_manager.execute_query(query, (student_id,))
                if result:
                    student_data = result[0]
            
            if student_data:
                formatted_data = PrintHelper.format_student_data_for_print(student_data)
                print_manager.print_student_report(formatted_data, self)
            else:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات الطالب")
                
        except Exception as e:
            logging.error(f"خطأ في طباعة تقرير الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في طباعة التقرير:\\n{str(e)}")
    
    def export_students_pdf(self):
        """تصدير قائمة الطلاب إلى PDF"""
        try:
            if not self.current_students:
                QMessageBox.warning(self, "تحذير", "لا توجد بيانات للتصدير")
                return
            
            from PyQt5.QtWidgets import QFileDialog
            from core.printing import TemplateType
            
            # اختيار مكان الحفظ
            file_path, _ = QFileDialog.getSaveFileName(
                self, "حفظ قائمة الطلاب", 
                f"قائمة_الطلاب_{len(self.current_students)}_طالب.pdf",
                "PDF Files (*.pdf)"
            )
            
            if file_path:
                students_data = PrintHelper.format_students_list_for_print(self.current_students)
                filter_info = self.get_current_filters_info()
                
                data = {
                    'students': students_data,
                    'filter_info': filter_info
                }
                
                print_manager.export_to_pdf(TemplateType.STUDENT_LIST, data, file_path, self)
                
        except Exception as e:
            logging.error(f"خطأ في تصدير PDF: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في التصدير:\\n{str(e)}")
    
    def get_current_data_for_print(self):
        """الحصول على البيانات الحالية للطباعة السريعة"""
        return PrintHelper.format_students_list_for_print(self.current_students)
    
    def get_current_filters_info(self):
        """الحصول على معلومات الفلاتر الحالية"""
        try:
            filters = {
                'school': self.school_combo.currentText(),
                'grade': self.grade_combo.currentText(),
                'status': self.status_combo.currentText(),
                'gender': self.gender_combo.currentText(),
                'search': self.search_input.text().strip()
            }
            
            return PrintHelper.create_filter_info_string(filters)
            
        except Exception as e:
            logging.error(f"خطأ في الحصول على معلومات الفلاتر: {e}")
            return "خطأ في الفلاتر"
