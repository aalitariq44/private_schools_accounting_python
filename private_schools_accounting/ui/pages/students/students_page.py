#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
صفحة إدارة الطلاب
"""

import logging
import json
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QFrame, QMessageBox, QHeaderView, QAbstractItemView,
    QMenu, QComboBox, QDateEdit, QSpinBox, QAction
)
from PyQt5.QtCore import Qt, pyqtSignal, QDate
from PyQt5.QtGui import QFont, QPixmap, QIcon

from core.database.connection import db_manager
from core.utils.logger import log_user_action, log_database_operation

# استيراد نوافذ إدارة الطلاب
from .add_student_dialog import AddStudentDialog
from .edit_student_dialog import EditStudentDialog


class StudentsPage(QWidget):
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
        self.load_schools()
        
        log_user_action("فتح صفحة إدارة الطلاب")
    
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
            
            # جدول الطلاب
            self.create_students_table(layout)
            
            # إحصائيات سريعة
            self.create_quick_stats(layout)
            
            self.setLayout(layout)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد واجهة صفحة الطلاب: {e}")
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
            
            title_label = QLabel("إدارة الطلاب")
            title_label.setObjectName("pageTitle")
            text_layout.addWidget(title_label)
            
            desc_label = QLabel("إدارة معلومات الطلاب والتسجيل والإحصائيات")
            desc_label.setObjectName("pageDesc")
            text_layout.addWidget(desc_label)
            
            header_layout.addLayout(text_layout)
            header_layout.addStretch()
            
            # إحصائيات سريعة في الرأس
            stats_layout = QHBoxLayout()
            
            self.total_students_label = QLabel("إجمالي الطلاب: 0")
            self.total_students_label.setObjectName("quickStat")
            stats_layout.addWidget(self.total_students_label)
            
            self.active_students_label = QLabel("الطلاب النشطون: 0")
            self.active_students_label.setObjectName("quickStat")
            stats_layout.addWidget(self.active_students_label)
            
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
            
            # الصف الأول - فلاتر
            filters_layout = QHBoxLayout()
            
            # اختيار المدرسة
            school_label = QLabel("المدرسة:")
            school_label.setObjectName("filterLabel")
            filters_layout.addWidget(school_label)
            
            self.school_combo = QComboBox()
            self.school_combo.setObjectName("filterCombo")
            self.school_combo.setMinimumWidth(200)
            filters_layout.addWidget(self.school_combo)
            
            # فلتر الصف
            grade_label = QLabel("الصف:")
            grade_label.setObjectName("filterLabel")
            filters_layout.addWidget(grade_label)
            
            self.grade_combo = QComboBox()
            self.grade_combo.setObjectName("filterCombo")
            self.grade_combo.addItem("جميع الصفوف", "")
            self.grade_combo.addItems([
                "الأول الابتدائي", "الثاني الابتدائي", "الثالث الابتدائي",
                "الرابع الابتدائي", "الخامس الابتدائي", "السادس الابتدائي",
                "الأول المتوسط", "الثاني المتوسط", "الثالث المتوسط",
                "الرابع الإعدادي", "الخامس الإعدادي", "السادس الإعدادي"
            ])
            filters_layout.addWidget(self.grade_combo)
            
            # فلتر الحالة
            status_label = QLabel("الحالة:")
            status_label.setObjectName("filterLabel")
            filters_layout.addWidget(status_label)
            
            self.status_combo = QComboBox()
            self.status_combo.setObjectName("filterCombo")
            self.status_combo.addItems(["جميع الحالات", "نشط", "منقطع", "متخرج"])
            filters_layout.addWidget(self.status_combo)
            
            filters_layout.addStretch()
            
            toolbar_layout.addLayout(filters_layout)
            
            # الصف الثاني - البحث والأزرار
            actions_layout = QHBoxLayout()
            
            # البحث
            search_label = QLabel("البحث:")
            search_label.setObjectName("filterLabel")
            actions_layout.addWidget(search_label)
            
            self.search_input = QLineEdit()
            self.search_input.setObjectName("searchInput")
            self.search_input.setPlaceholderText("ابحث عن الطلاب بالاسم أو رقم الهوية...")
            self.search_input.setMinimumWidth(300)
            actions_layout.addWidget(self.search_input)
            
            actions_layout.addStretch()
            
            # أزرار العمليات
            self.add_student_button = QPushButton("إضافة طالب")
            self.add_student_button.setObjectName("primaryButton")
            actions_layout.addWidget(self.add_student_button)
            
            self.import_students_button = QPushButton("استيراد قائمة")
            self.import_students_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.import_students_button)
            
            self.export_students_button = QPushButton("تصدير القائمة")
            self.export_students_button.setObjectName("secondaryButton")
            actions_layout.addWidget(self.export_students_button)
            
            self.refresh_button = QPushButton("تحديث")
            self.refresh_button.setObjectName("refreshButton")
            actions_layout.addWidget(self.refresh_button)
            
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
            table_layout.setContentsMargins(0, 0, 0, 0)
            
            # إنشاء الجدول
            self.students_table = QTableWidget()
            self.students_table.setObjectName("dataTable")
            
            # إعداد الأعمدة
            columns = [
                "المعرف", "الاسم الكامل", "المدرسة", 
                "الصف", "الشعبة", "الجنس",
                "الهاتف", "الحالة", "تاريخ المباشرة"
            ]
            
            self.students_table.setColumnCount(len(columns))
            self.students_table.setHorizontalHeaderLabels(columns)
            
            # إعداد خصائص الجدول
            self.students_table.setAlternatingRowColors(True)
            self.students_table.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.students_table.setSelectionMode(QAbstractItemView.SingleSelection)
            self.students_table.setSortingEnabled(True)
            self.students_table.setShowGrid(False)
            
            # تخصيص عرض الأعمدة
            header = self.students_table.horizontalHeader()
            header.setStretchLastSection(True)
            header.setDefaultSectionSize(120)
            header.resizeSection(0, 80)   # المعرف
            header.resizeSection(1, 150)  # الاسم الكامل
            header.resizeSection(2, 130)  # المدرسة
            header.resizeSection(3, 100)  # الصف
            header.resizeSection(4, 80)   # الشعبة
            header.resizeSection(5, 80)   # الجنس
            header.resizeSection(6, 110)  # الهاتف
            header.resizeSection(7, 80)   # الحالة
            
            # إخفاء العمود الأول (المعرف) 
            self.students_table.setColumnHidden(0, True)
            
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
        """إنشاء إحصائيات سريعة أسفل الجدول"""
        try:
            stats_frame = QFrame()
            stats_frame.setObjectName("statsFrame")
            
            stats_layout = QHBoxLayout(stats_frame)
            stats_layout.setContentsMargins(15, 10, 15, 10)
            
            # عدد الطلاب المعروضين
            self.displayed_count_label = QLabel("عدد الطلاب المعروضين: 0")
            self.displayed_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.displayed_count_label)
            
            stats_layout.addStretch()
            
            # إجماليات سريعة
            self.male_count_label = QLabel("ذكور: 0")
            self.male_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.male_count_label)
            
            self.female_count_label = QLabel("إناث: 0")
            self.female_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.female_count_label)
            
            self.active_count_label = QLabel("نشط: 0")
            self.active_count_label.setObjectName("statLabel")
            stats_layout.addWidget(self.active_count_label)
            
            layout.addWidget(stats_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء الإحصائيات السريعة: {e}")
    
    def setup_connections(self):
        """ربط الإشارات والأحداث"""
        try:
            # ربط أزرار العمليات
            self.add_student_button.clicked.connect(self.add_student)
            self.import_students_button.clicked.connect(self.import_students)
            self.export_students_button.clicked.connect(self.export_students)
            self.refresh_button.clicked.connect(self.refresh)
            
            # ربط الفلاتر
            self.school_combo.currentTextChanged.connect(self.apply_filters)
            self.grade_combo.currentTextChanged.connect(self.apply_filters)
            self.status_combo.currentTextChanged.connect(self.apply_filters)
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
                    self.school_combo.addItem(school[1], school[0])
            
            # تحميل الطلاب بعد تحميل المدارس
            self.refresh()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
    
    def load_students(self):
        """تحميل قائمة الطلاب"""
        try:
            # بناء الاستعلام مع الفلاتر
            query = """
                SELECT s.id, s.full_name, sc.name_ar as school_name,
                       s.grade, s.section, s.gender,
                       s.phone, s.status, s.start_date
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
            
            # فلتر البحث
            search_text = self.search_input.text().strip()
            if search_text:
                query += " AND (s.full_name LIKE ?)"
                search_param = f"%{search_text}%"
                params.append(search_param)
            
            query += " ORDER BY s.created_at DESC"
            
            # تنفيذ الاستعلام
            students = db_manager.execute_query(query, params)
            
            self.current_students = students or []
            self.populate_students_table()
            self.update_stats()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الطلاب: {e}")
            self.show_error_message("خطأ في التحميل", f"حدث خطأ في تحميل بيانات الطلاب: {str(e)}")
    
    def populate_students_table(self):
        """ملء جدول الطلاب"""
        try:
            self.students_table.setRowCount(len(self.current_students))
            
            for row, student in enumerate(self.current_students):
                # المعرف (مخفي)
                self.students_table.setItem(row, 0, QTableWidgetItem(str(student[0])))
                
                # الاسم الكامل
                self.students_table.setItem(row, 1, QTableWidgetItem(student[1] or ""))
                
                # المدرسة
                self.students_table.setItem(row, 2, QTableWidgetItem(student[2] or "غير محدد"))
                
                # الصف
                self.students_table.setItem(row, 3, QTableWidgetItem(student[3] or ""))
                
                # الشعبة
                self.students_table.setItem(row, 4, QTableWidgetItem(student[4] or ""))
                
                # الجنس
                self.students_table.setItem(row, 5, QTableWidgetItem(student[5] or ""))
                
                # الهاتف
                self.students_table.setItem(row, 6, QTableWidgetItem(student[6] or ""))
                
                # الحالة
                status_item = QTableWidgetItem(student[7] or "نشط")
                if student[7] == "نشط":
                    status_item.setBackground(Qt.green)
                elif student[7] == "منقطع":
                    status_item.setBackground(Qt.red)
                elif student[7] == "متخرج":
                    status_item.setBackground(Qt.blue)
                self.students_table.setItem(row, 7, status_item)
                
                # تاريخ المباشرة
                start_date = student[8]
                if start_date:
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        formatted_date = date_obj.strftime("%Y-%m-%d")
                    except:
                        formatted_date = str(start_date)[:10]
                else:
                    formatted_date = ""
                
                self.students_table.setItem(row, 8, QTableWidgetItem(formatted_date))
            
            # تحديث إحصائية العدد المعروض
            self.displayed_count_label.setText(f"عدد الطلاب المعروضين: {len(self.current_students)}")
            
        except Exception as e:
            logging.error(f"خطأ في ملء جدول الطلاب: {e}")
    
    def update_stats(self):
        """تحديث الإحصائيات"""
        try:
            # إحصائيات عامة
            total_query = "SELECT COUNT(*) FROM students"
            total_count = db_manager.execute_query(total_query)
            total_count = total_count[0] if total_count else 0
            
            active_query = "SELECT COUNT(*) FROM students WHERE status = 'نشط'"
            active_count = db_manager.execute_query(active_query)
            active_count = active_count[0] if active_count else 0
            
            self.total_students_label.setText(f"إجمالي الطلاب: {total_count}")
            self.active_students_label.setText(f"الطلاب النشطون: {active_count}")
            
            # إحصائيات الطلاب المعروضين حالياً
            if self.current_students:
                # حساب الجنس (سيحتاج لحقل الجنس في قاعدة البيانات)
                male_count = 0
                female_count = 0
                active_displayed = 0
                
                for student in self.current_students:
                    if student[8] == "نشط":
                        active_displayed += 1
                
                self.male_count_label.setText(f"ذكور: {male_count}")
                self.female_count_label.setText(f"إناث: {female_count}")
                self.active_count_label.setText(f"نشط: {active_displayed}")
            else:
                self.male_count_label.setText("ذكور: 0")
                self.female_count_label.setText("إناث: 0")
                self.active_count_label.setText("نشط: 0")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الإحصائيات: {e}")
    
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
            if self.students_table.itemAt(position):
                menu = QMenu()
                
                edit_action = QAction("تعديل الطالب", self)
                edit_action.triggered.connect(lambda: self.edit_selected_student())
                menu.addAction(edit_action)
                
                view_action = QAction("عرض تفاصيل الطالب", self)
                view_action.triggered.connect(lambda: self.view_student_details())
                menu.addAction(view_action)
                
                menu.addSeparator()
                
                deactivate_action = QAction("إيقاف الطالب", self)
                deactivate_action.triggered.connect(lambda: self.change_student_status("منقطع"))
                menu.addAction(deactivate_action)
                
                graduate_action = QAction("تخريج الطالب", self)
                graduate_action.triggered.connect(lambda: self.change_student_status("متخرج"))
                menu.addAction(graduate_action)
                
                menu.addSeparator()
                
                delete_action = QAction("حذف الطالب", self)
                delete_action.triggered.connect(lambda: self.delete_selected_student())
                menu.addAction(delete_action)
                
                menu.exec_(self.students_table.mapToGlobal(position))
            
        except Exception as e:
            logging.error(f"خطأ في عرض قائمة السياق: {e}")
    
    def add_student(self):
        """إضافة طالب جديد"""
        try:
            dialog = AddStudentDialog(self)
            dialog.student_added.connect(self.refresh)
            dialog.exec_()
            log_user_action("طلب إضافة طالب جديد")
            
        except Exception as e:
            logging.error(f"خطأ في إضافة طالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة إضافة الطالب:\n{str(e)}")
    
    def edit_student(self, row, column):
        """تعديل طالب عند الضغط المزدوج"""
        try:
            if row >= 0:
                student_id = int(self.students_table.item(row, 0).text())
                self.edit_student_by_id(student_id)
                
        except Exception as e:
            logging.error(f"خطأ في تعديل الطالب: {e}")
    
    def edit_selected_student(self):
        """تعديل الطالب المحدد"""
        try:
            current_row = self.students_table.currentRow()
            if current_row >= 0:
                student_id = int(self.students_table.item(current_row, 0).text())
                self.edit_student_by_id(student_id)
            
        except Exception as e:
            logging.error(f"خطأ في تعديل الطالب المحدد: {e}")
    
    def edit_student_by_id(self, student_id: int):
        """تعديل طالب بالمعرف"""
        try:
            dialog = EditStudentDialog(student_id, self)
            dialog.student_updated.connect(self.refresh)
            dialog.exec_()
            log_user_action("طلب تعديل طالب", f"المعرف: {student_id}")
            
        except Exception as e:
            logging.error(f"خطأ في تعديل الطالب {student_id}: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في فتح نافذة تعديل الطالب:\n{str(e)}")
    
    def view_student_details(self):
        """عرض تفاصيل الطالب"""
        try:
            current_row = self.students_table.currentRow()
            if current_row >= 0:
                student_id = int(self.students_table.item(current_row, 0).text())
                self.show_info_message("قيد التطوير", f"نافذة تفاصيل الطالب {student_id} قيد التطوير")
                log_user_action("طلب عرض تفاصيل طالب", f"المعرف: {student_id}")
            
        except Exception as e:
            logging.error(f"خطأ في عرض تفاصيل الطالب: {e}")
    
    def change_student_status(self, new_status):
        """تغيير حالة الطالب"""
        try:
            current_row = self.students_table.currentRow()
            if current_row >= 0:
                student_id = int(self.students_table.item(current_row, 0).text())
                student_name = self.students_table.item(current_row, 1).text()
                
                reply = QMessageBox.question(
                    self,
                    "تأكيد التغيير",
                    f"هل تريد تغيير حالة الطالب '{student_name}' إلى '{new_status}'؟",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    update_query = "UPDATE students SET status = ? WHERE id = ?"
                    success = db_manager.execute_query(update_query, (new_status, student_id))
                    
                    if success:
                        log_database_operation("تحديث", "students", f"تغيير حالة الطالب {student_name} إلى {new_status}")
                        log_user_action("تغيير حالة طالب", f"{student_name} -> {new_status}")
                        self.refresh()
                        self.show_info_message("تم التحديث", f"تم تغيير حالة الطالب إلى '{new_status}' بنجاح")
                    else:
                        self.show_error_message("خطأ", "فشل في تغيير حالة الطالب")
            
        except Exception as e:
            logging.error(f"خطأ في تغيير حالة الطالب: {e}")
            self.show_error_message("خطأ", f"حدث خطأ في تغيير حالة الطالب: {str(e)}")
    
    def delete_selected_student(self):
        """حذف الطالب المحدد"""
        try:
            current_row = self.students_table.currentRow()
            if current_row >= 0:
                student_id = int(self.students_table.item(current_row, 0).text())
                student_name = self.students_table.item(current_row, 1).text()
                
                reply = QMessageBox.question(
                    self,
                    "تأكيد الحذف",
                    f"هل تريد حذف الطالب '{student_name}' نهائياً؟\n\nتحذير: هذا الإجراء لا يمكن التراجع عنه!",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    delete_query = "DELETE FROM students WHERE id = ?"
                    success = db_manager.execute_query(delete_query, (student_id,))
                    
                    if success:
                        log_database_operation("حذف", "students", f"حذف الطالب: {student_name}")
                        log_user_action("حذف طالب", student_name)
                        self.refresh()
                        self.show_info_message("تم الحذف", f"تم حذف الطالب '{student_name}' بنجاح")
                    else:
                        self.show_error_message("خطأ", "فشل في حذف الطالب")
            
        except Exception as e:
            logging.error(f"خطأ في حذف الطالب: {e}")
            self.show_error_message("خطأ", f"حدث خطأ في حذف الطالب: {str(e)}")
    
    def import_students(self):
        """استيراد قائمة طلاب"""
        try:
            self.show_info_message("قيد التطوير", "ميزة استيراد الطلاب قيد التطوير")
            log_user_action("طلب استيراد قائمة طلاب")
            
        except Exception as e:
            logging.error(f"خطأ في استيراد الطلاب: {e}")
    
    def export_students(self):
        """تصدير قائمة الطلاب"""
        try:
            self.show_info_message("قيد التطوير", "ميزة تصدير الطلاب قيد التطوير")
            log_user_action("طلب تصدير قائمة طلاب")
            
        except Exception as e:
            logging.error(f"خطأ في تصدير الطلاب: {e}")
    
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
                        stop:0 #3498DB, stop:1 #2980B9);
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
                    color: #E8F4FD;
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
                    border-color: #3498DB;
                    outline: none;
                }
                
                #searchInput {
                    padding: 8px 12px;
                    border: 2px solid #3498DB;
                    border-radius: 6px;
                    font-size: 13px;
                    background-color: white;
                }
                
                #searchInput:focus {
                    border-color: #2980B9;
                    outline: none;
                }
                
                /* الأزرار */
                #primaryButton {
                    background-color: #27AE60;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 100px;
                }
                
                #primaryButton:hover {
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
                    background-color: #E3F2FD;
                    color: #1976D2;
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
                
                /* إطار الإحصائيات */
                #statsFrame {
                    background-color: white;
                    border: 1px solid #E9ECEF;
                    border-radius: 8px;
                    margin-top: 10px;
                }
                
                #statLabel {
                    font-size: 12px;
                    font-weight: bold;
                    color: #2C3E50;
                    margin: 0 10px;
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
            logging.error(f"خطأ في إعداد تنسيقات صفحة الطلاب: {e}")
