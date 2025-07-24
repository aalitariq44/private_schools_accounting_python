#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
                            QPushButton, QFrame, QMessageBox, QFileDialog,
                            QGroupBox, QSpinBox, QScrollArea)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon
import shutil
import uuid
from datetime import datetime
import logging

# Import the database manager
from core.database.connection import db_manager

class EditStudentDialog(QDialog):
    student_updated = pyqtSignal()
    
    def __init__(self, student_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.photo_path = None
        self.current_photo = None
        self.setup_ui()
        self.load_schools()
        self.load_student_data()
        self.setup_connections()
        
    def setup_ui(self):
        self.setWindowTitle("تعديل بيانات الطالب")
        self.setModal(True)
        self.resize(800, 900)
        
        # تطبيق الستايل مع تحسينات
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fff5f5, stop:1 #ffe8e8);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 24px;
                margin: 5px 0px;
            }
            
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox {
                padding: 12px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                background-color: white;
                font-size: 24px;
                min-height: 30px;
                margin: 5px 0px;
            }
            
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus {
                border-color: #e74c3c;
                background-color: #fff8f8;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 24px;
                min-width: 120px;
                margin: 8px 4px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ec7063, stop:1 #e74c3c);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c0392b, stop:1 #a93226);
            }
            
            QPushButton#save_btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #2ecc71);
            }
            
            QPushButton#save_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ecc71, stop:1 #58d68d);
            }
            
            QPushButton#cancel_btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #95a5a6, stop:1 #7f8c8d);
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 24px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 12px;
                margin: 15px 0px;
                padding-top: 20px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 20px;
                padding: 0 10px 0 10px;
                background-color: #e74c3c;
                color: white;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 24px;
            }
            
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # إضافة scroll area للشاشات الصغيرة
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # المحتوى الرئيسي داخل scroll area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(25, 25, 25, 25)
        
        # عنوان النافذة
        title_label = QLabel("تعديل بيانات الطالب")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                padding: 15px;
                border-radius: 10px;
                font-size: 28px;
                font-weight: bold;
            }
        """)
        content_layout.addWidget(title_label)
        
        # مجموعة المعلومات الأساسية
        basic_info_group = QGroupBox("المعلومات الأساسية")
        basic_layout = QFormLayout(basic_info_group)
        basic_layout.setSpacing(15)
        
        # الحقول الأساسية
        self.full_name_edit = QLineEdit()
        self.full_name_edit.setPlaceholderText("أدخل الاسم الكامل للطالب")
        basic_layout.addRow("الاسم الكامل:", self.full_name_edit)
        
        # الرقم الوطني
        self.national_id_edit = QLineEdit()
        self.national_id_edit.setPlaceholderText("رقم الهوية أو شهادة الميلاد")
        basic_layout.addRow("الرقم الوطني:", self.national_id_edit)
        
        # الجنس
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["ذكر", "أنثى"])
        basic_layout.addRow("الجنس:", self.gender_combo)
        
        content_layout.addWidget(basic_info_group)
        
        # مجموعة المعلومات الأكاديمية
        academic_info_group = QGroupBox("المعلومات الأكاديمية")
        academic_layout = QFormLayout(academic_info_group)
        academic_layout.setSpacing(15)
        
        # المدرسة
        self.school_combo = QComboBox()
        self.school_combo.setPlaceholderText("اختر المدرسة")
        academic_layout.addRow("المدرسة:", self.school_combo)
        
        # الصف
        self.grade_combo = QComboBox()
        self.grade_combo.setPlaceholderText("اختر الصف")
        academic_layout.addRow("الصف:", self.grade_combo)
        
        # الشعبة
        self.section_edit = QLineEdit()
        self.section_edit.setPlaceholderText("مثل: أ، ب، ج")
        academic_layout.addRow("الشعبة:", self.section_edit)
        
        # السنة الدراسية
        self.academic_year_edit = QLineEdit()
        self.academic_year_edit.setPlaceholderText("مثل: 2024-2025")
        academic_layout.addRow("السنة الدراسية:", self.academic_year_edit)
        
        # المبلغ الإجمالي
        self.total_fee_edit = QLineEdit()
        self.total_fee_edit.setPlaceholderText("المبلغ الإجمالي بالدينار")
        academic_layout.addRow("الرسوم الدراسية:", self.total_fee_edit)
        
        # تاريخ المباشرة
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        academic_layout.addRow("تاريخ المباشرة:", self.start_date_edit)
        
        # الحالة
        self.status_combo = QComboBox()
        self.status_combo.addItems(["نشط", "منقطع", "متخرج", "محول"])
        academic_layout.addRow("الحالة:", self.status_combo)
        
        content_layout.addWidget(academic_info_group)
        
        # مجموعة معلومات الاتصال وولي الأمر
        contact_info_group = QGroupBox("معلومات الاتصال وولي الأمر")
        contact_layout = QFormLayout(contact_info_group)
        contact_layout.setSpacing(15)
        
        # الهاتف
        self.phone_edit = QLineEdit()
        self.phone_edit.setPlaceholderText("رقم هاتف الطالب")
        contact_layout.addRow("هاتف الطالب:", self.phone_edit)
        
        # اسم ولي الأمر
        self.guardian_name_edit = QLineEdit()
        self.guardian_name_edit.setPlaceholderText("اسم ولي الأمر")
        contact_layout.addRow("اسم ولي الأمر:", self.guardian_name_edit)
        
        # هاتف ولي الأمر
        self.guardian_phone_edit = QLineEdit()
        self.guardian_phone_edit.setPlaceholderText("رقم هاتف ولي الأمر")
        contact_layout.addRow("هاتف ولي الأمر:", self.guardian_phone_edit)
        
        content_layout.addWidget(contact_info_group)
        
        # أزرار العمل
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_btn = QPushButton("حفظ التعديلات")
        self.save_btn.setObjectName("save_btn")
        buttons_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancel_btn")
        buttons_layout.addWidget(self.cancel_btn)
        
        content_layout.addLayout(buttons_layout)
        
        # إضافة المحتوى إلى scroll area
        scroll_area.setWidget(content_widget)
        main_layout.addWidget(scroll_area)
        
    def setup_connections(self):
        """ربط الإشارات"""
        self.save_btn.clicked.connect(self.save_student)
        self.cancel_btn.clicked.connect(self.reject)
        self.school_combo.currentTextChanged.connect(self.update_grades_for_school)
        
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            query = "SELECT id, name_ar, school_types FROM schools ORDER BY name_ar"
            schools = db_manager.execute_query(query)
            
            self.school_combo.clear()
            self.school_combo.addItem("اختر المدرسة", None)
            
            for school in schools:
                school_data = {
                    'id': school['id'],
                    'name': school['name_ar'],
                    'types': school['school_types']
                }
                self.school_combo.addItem(school['name_ar'], school_data)
                
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل المدارس:\\n{str(e)}")
    
    def update_grades_for_school(self):
        """تحديث قائمة الصفوف بناءً على نوع المدرسة المختارة"""
        try:
            current_grade = self.grade_combo.currentText()  # حفظ الصف الحالي
            self.grade_combo.clear()
            
            if self.school_combo.currentIndex() <= 0:
                return
                
            school_data = self.school_combo.currentData()
            if not school_data:
                return
                
            school_types_str = school_data.get('types', '')
            
            # تحليل أنواع المدرسة
            try:
                school_types = json.loads(school_types_str) if school_types_str else []
            except:
                school_types = [school_types_str] if school_types_str else []
            
            # قائمة الصفوف
            all_grades = []
            
            # إضافة الصفوف حسب نوع المدرسة
            if "ابتدائي" in school_types:
                all_grades.extend([
                    "الأول الابتدائي", "الثاني الابتدائي", "الثالث الابتدائي",
                    "الرابع الابتدائي", "الخامس الابتدائي", "السادس الابتدائي"
                ])
            
            if "متوسط" in school_types:
                all_grades.extend([
                    "الأول المتوسط", "الثاني المتوسط", "الثالث المتوسط"
                ])
            
            if "إعدادي" in school_types or "ثانوي" in school_types:
                all_grades.extend([
                    "الرابع العلمي", "الرابع الأدبي",
                    "الخامس العلمي", "الخامس الأدبي", 
                    "السادس العلمي", "السادس الأدبي"
                ])
            
            # إضافة الصفوف إلى القائمة
            self.grade_combo.addItem("اختر الصف", None)
            for grade in all_grades:
                self.grade_combo.addItem(grade, grade)
            
            # إعادة تعيين الصف الحالي إذا كان موجوداً
            if current_grade:
                index = self.grade_combo.findText(current_grade)
                if index != -1:
                    self.grade_combo.setCurrentIndex(index)
                
        except Exception as e:
            logging.error(f"خطأ في تحديث الصفوف: {e}")
    
    def load_student_data(self):
        """تحميل بيانات الطالب الحالي"""
        try:
            query = """
                SELECT s.*, sc.name_ar as school_name, sc.school_types
                FROM students s
                LEFT JOIN schools sc ON s.school_id = sc.id
                WHERE s.id = ?
            """
            result = db_manager.execute_query(query, (self.student_id,))
            
            if not result:
                QMessageBox.warning(self, "خطأ", "لم يتم العثور على بيانات الطالب")
                self.reject()
                return
            
            student = result[0]
            
            # ملء الحقول بالبيانات الحالية
            self.full_name_edit.setText(student['name'] or "")
            self.national_id_edit.setText(student['national_id_number'] or "")
            
            # تحديد الجنس
            if student['gender']:
                index = self.gender_combo.findText(student['gender'])
                if index != -1:
                    self.gender_combo.setCurrentIndex(index)
            
            # تحديد المدرسة
            if student['school_id']:
                for i in range(self.school_combo.count()):
                    school_data = self.school_combo.itemData(i)
                    if school_data and school_data['id'] == student['school_id']:
                        self.school_combo.setCurrentIndex(i)
                        break
            
            # تحديث الصفوف بناءً على المدرسة المختارة
            self.update_grades_for_school()
            
            # تحديد الصف
            if student['grade']:
                index = self.grade_combo.findText(student['grade'])
                if index != -1:
                    self.grade_combo.setCurrentIndex(index)
            
            self.section_edit.setText(student['section'] or "")
            self.academic_year_edit.setText(student['academic_year'] or "")
            self.total_fee_edit.setText(str(student['total_fee']) if student['total_fee'] else "")
            
            # تاريخ المباشرة
            if student['start_date']:
                try:
                    date = QDate.fromString(student['start_date'], "yyyy-MM-dd")
                    self.start_date_edit.setDate(date)
                except:
                    pass
            
            # تحديد الحالة
            if student['status']:
                index = self.status_combo.findText(student['status'])
                if index != -1:
                    self.status_combo.setCurrentIndex(index)
            
            self.phone_edit.setText(student['phone'] or "")
            self.guardian_name_edit.setText(student['guardian_name'] or "")
            self.guardian_phone_edit.setText(student['guardian_phone'] or "")
            
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تحميل بيانات الطالب:\\n{str(e)}")
    
    def validate_inputs(self):
        """التحقق من صحة البيانات المدخلة"""
        errors = []
        
        # التحقق من الحقول المطلوبة
        if not self.full_name_edit.text().strip():
            errors.append("الاسم الكامل للطالب مطلوب")
            
        if self.school_combo.currentIndex() <= 0:
            errors.append("يجب اختيار المدرسة")
            
        if self.grade_combo.currentIndex() <= 0:
            errors.append("يجب اختيار الصف")
            
        if not self.section_edit.text().strip():
            errors.append("الشعبة مطلوبة")
        
        # التحقق من الرسوم
        try:
            if self.total_fee_edit.text().strip():
                float(self.total_fee_edit.text().strip())
        except ValueError:
            errors.append("يجب أن تكون الرسوم رقماً صحيحاً")
        
        return errors
    
    def save_student(self):
        """حفظ تعديلات بيانات الطالب"""
        # التحقق من صحة البيانات
        errors = self.validate_inputs()
        if errors:
            QMessageBox.warning(self, "خطأ في البيانات", "\\n".join(errors))
            return
        
        try:
            school_data = self.school_combo.currentData()
            
            # تحديث البيانات في قاعدة البيانات
            update_query = """
                UPDATE students SET
                    name = ?, national_id_number = ?, school_id = ?, grade = ?,
                    section = ?, academic_year = ?, gender = ?, phone = ?,
                    guardian_name = ?, guardian_phone = ?, total_fee = ?,
                    start_date = ?, status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """
            
            total_fee = 0.0
            if self.total_fee_edit.text().strip():
                total_fee = float(self.total_fee_edit.text().strip())
            
            student_data = (
                self.full_name_edit.text().strip(),
                self.national_id_edit.text().strip(),
                school_data['id'],
                self.grade_combo.currentData(),
                self.section_edit.text().strip(),
                self.academic_year_edit.text().strip() or f"{datetime.now().year}-{datetime.now().year + 1}",
                self.gender_combo.currentText(),
                self.phone_edit.text().strip(),
                self.guardian_name_edit.text().strip(),
                self.guardian_phone_edit.text().strip(),
                total_fee,
                self.start_date_edit.date().toString("yyyy-MM-dd"),
                self.status_combo.currentText(),
                self.student_id
            )
            
            affected_rows = db_manager.execute_update(update_query, student_data)
            
            if affected_rows > 0:
                QMessageBox.information(self, "نجح", "تم تحديث بيانات الطالب بنجاح!")
                self.student_updated.emit()
                self.accept()
            else:
                QMessageBox.warning(self, "خطأ", "لم يتم تحديث أي بيانات")
            
        except Exception as e:
            logging.error(f"خطأ في تحديث الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تحديث البيانات:\\n{str(e)}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # تطبيق الخط العربي
    font = QFont("Arial", 24)
    app.setFont(font)
    
    # لاختبار النافذة (يجب توفير معرف طالب صحيح)
    dialog = EditStudentDialog(1)  # افتراض أن هناك طالب بمعرف 1
    dialog.show()
    
    sys.exit(app.exec_())
