import sys
import os
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, 
                            QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
                            QPushButton, QFrame, QMessageBox, QFileDialog,
                            QGroupBox, QSpinBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon
import sqlite3
import shutil
import uuid
from datetime import datetime
import logging

class EditStudentDialog(QDialog):
    student_updated = pyqtSignal()
    
    def __init__(self, student_id, parent=None):
        super().__init__(parent)
        self.student_id = student_id
        self.db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), 'database', 'private_schools.db')
        self.photo_path = None
        self.current_photo = None
        self.setup_ui()
        self.load_schools()
        self.load_student_data()
        self.setup_connections()
        
    def setup_ui(self):
        self.setWindowTitle("تعديل بيانات الطالب")
        self.setModal(True)
        self.resize(700, 800)
        
        # تطبيق الستايل (نفس ستايل إضافة الطالب مع تعديلات للتحديث)
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #fff5f5, stop:1 #ffe8e8);
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            
            QLabel {
                color: #2c3e50;
                font-weight: bold;
                font-size: 11px;
            }
            
            QLineEdit, QComboBox, QDateEdit, QTextEdit, QSpinBox {
                padding: 8px 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
                font-size: 11px;
                min-height: 20px;
            }
            
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus, QSpinBox:focus {
                border-color: #e74c3c;
                background-color: #fff8f8;
            }
            
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }
            
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #ec7063, stop:1 #e74c3c);
                transform: translateY(-2px);
            }
            
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #c0392b, stop:1 #a93226);
            }
            
            QPushButton#photo_btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #27ae60, stop:1 #2ecc71);
                min-width: 80px;
            }
            
            QPushButton#photo_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #2ecc71, stop:1 #58d68d);
            }
            
            QPushButton#cancel_btn {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #95a5a6, stop:1 #7f8c8d);
            }
            
            QPushButton#cancel_btn:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #b2bec3, stop:1 #95a5a6);
            }
            
            QGroupBox {
                font-weight: bold;
                font-size: 12px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin: 10px 0px;
                padding-top: 15px;
            }
            
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            
            QFrame {
                background-color: white;
                border: 2px solid #ecf0f1;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        # التخطيط الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
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
                font-size: 18px;
                font-weight: bold;
            }
        """)
        main_layout.addWidget(title_label)
        
        # مجموعة المعلومات الأساسية
        basic_info_group = QGroupBox("المعلومات الأساسية")
        basic_layout = QFormLayout(basic_info_group)
        basic_layout.setSpacing(12)
        
        # الحقول الأساسية
        self.first_name_edit = QLineEdit()
        self.first_name_edit.setPlaceholderText("أدخل الاسم الأول")
        basic_layout.addRow("الاسم الأول (عربي):", self.first_name_edit)
        
        self.first_name_en_edit = QLineEdit()
        self.first_name_en_edit.setPlaceholderText("Enter first name")
        basic_layout.addRow("الاسم الأول (إنجليزي):", self.first_name_en_edit)
        
        self.last_name_edit = QLineEdit()
        self.last_name_edit.setPlaceholderText("أدخل الاسم الأخير")
        basic_layout.addRow("الاسم الأخير (عربي):", self.last_name_edit)
        
        self.last_name_en_edit = QLineEdit()
        self.last_name_en_edit.setPlaceholderText("Enter last name")
        basic_layout.addRow("الاسم الأخير (إنجليزي):", self.last_name_en_edit)
        
        # تاريخ الميلاد
        self.birth_date_edit = QDateEdit()
        self.birth_date_edit.setCalendarPopup(True)
        self.birth_date_edit.setDisplayFormat("yyyy-MM-dd")
        basic_layout.addRow("تاريخ الميلاد:", self.birth_date_edit)
        
        # الجنس
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["ذكر", "أنثى"])
        basic_layout.addRow("الجنس:", self.gender_combo)
        
        # رقم الهوية
        self.national_id_edit = QLineEdit()
        self.national_id_edit.setPlaceholderText("أدخل رقم الهوية")
        basic_layout.addRow("رقم الهوية:", self.national_id_edit)
        
        main_layout.addWidget(basic_info_group)
        
        # مجموعة المعلومات الأكاديمية
        academic_info_group = QGroupBox("المعلومات الأكاديمية")
        academic_layout = QFormLayout(academic_info_group)
        academic_layout.setSpacing(12)
        
        # المدرسة
        self.school_combo = QComboBox()
        academic_layout.addRow("المدرسة:", self.school_combo)
        
        # الصف
        self.grade_combo = QComboBox()
        self.grade_combo.addItems([
            "KG1", "KG2", "الأول الابتدائي", "الثاني الابتدائي", "الثالث الابتدائي",
            "الرابع الابتدائي", "الخامس الابتدائي", "السادس الابتدائي",
            "الأول المتوسط", "الثاني المتوسط", "الثالث المتوسط",
            "الأول الثانوي", "الثاني الثانوي", "الثالث الثانوي"
        ])
        academic_layout.addRow("الصف:", self.grade_combo)
        
        # الشعبة
        self.section_edit = QLineEdit()
        self.section_edit.setPlaceholderText("مثال: أ، ب، ج")
        academic_layout.addRow("الشعبة:", self.section_edit)
        
        # رقم الطالب
        self.student_number_edit = QLineEdit()
        self.student_number_edit.setPlaceholderText("رقم الطالب في المدرسة")
        academic_layout.addRow("رقم الطالب:", self.student_number_edit)
        
        # سنة الالتحاق
        self.enrollment_year_spin = QSpinBox()
        self.enrollment_year_spin.setRange(2000, 2030)
        academic_layout.addRow("سنة الالتحاق:", self.enrollment_year_spin)
        
        # الحالة
        self.status_combo = QComboBox()
        self.status_combo.addItems(["نشط", "منقطع", "متخرج", "محول"])
        academic_layout.addRow("الحالة:", self.status_combo)
        
        main_layout.addWidget(academic_info_group)
        
        # مجموعة معلومات الاتصال
        contact_info_group = QGroupBox("معلومات الاتصال")
        contact_layout = QFormLayout(contact_info_group)
        contact_layout.setSpacing(12)
        
        # اسم ولي الأمر
        self.guardian_name_edit = QLineEdit()
        self.guardian_name_edit.setPlaceholderText("اسم ولي الأمر")
        contact_layout.addRow("اسم ولي الأمر:", self.guardian_name_edit)
        
        # هاتف ولي الأمر
        self.guardian_phone_edit = QLineEdit()
        self.guardian_phone_edit.setPlaceholderText("رقم الهاتف")
        contact_layout.addRow("هاتف ولي الأمر:", self.guardian_phone_edit)
        
        # العنوان
        self.address_edit = QTextEdit()
        self.address_edit.setPlaceholderText("العنوان التفصيلي")
        self.address_edit.setMaximumHeight(80)
        contact_layout.addRow("العنوان:", self.address_edit)
        
        main_layout.addWidget(contact_info_group)
        
        # مجموعة الصورة الشخصية
        photo_group = QGroupBox("الصورة الشخصية")
        photo_layout = QHBoxLayout(photo_group)
        
        # عرض الصورة
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(100, 100)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                border-radius: 10px;
                background-color: #f8f9fa;
                color: #6c757d;
                font-size: 10px;
            }
        """)
        self.photo_label.setAlignment(Qt.AlignCenter)
        self.photo_label.setText("لا توجد صورة")
        photo_layout.addWidget(self.photo_label)
        
        # أزرار الصورة
        photo_buttons_layout = QVBoxLayout()
        
        self.select_photo_btn = QPushButton("تغيير الصورة")
        self.select_photo_btn.setObjectName("photo_btn")
        photo_buttons_layout.addWidget(self.select_photo_btn)
        
        self.remove_photo_btn = QPushButton("إزالة الصورة")
        self.remove_photo_btn.setObjectName("cancel_btn")
        photo_buttons_layout.addWidget(self.remove_photo_btn)
        
        photo_buttons_layout.addStretch()
        photo_layout.addLayout(photo_buttons_layout)
        photo_layout.addStretch()
        
        main_layout.addWidget(photo_group)
        
        # أزرار العمل
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        self.save_btn = QPushButton("حفظ التعديلات")
        self.save_btn.setIcon(QIcon("💾"))
        buttons_layout.addWidget(self.save_btn)
        
        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.setObjectName("cancel_btn")
        self.cancel_btn.setIcon(QIcon("❌"))
        buttons_layout.addWidget(self.cancel_btn)
        
        main_layout.addLayout(buttons_layout)
        
    def setup_connections(self):
        """ربط الإشارات"""
        self.save_btn.clicked.connect(self.save_student)
        self.cancel_btn.clicked.connect(self.reject)
        self.select_photo_btn.clicked.connect(self.select_photo)
        self.remove_photo_btn.clicked.connect(self.remove_photo)
        
    def load_schools(self):
        """تحميل قائمة المدارس"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, arabic_name FROM schools ORDER BY arabic_name")
            schools = cursor.fetchall()
            
            self.school_combo.clear()
            for school_id, school_name in schools:
                self.school_combo.addItem(school_name, school_id)
                
            conn.close()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل المدارس: {e}")
            QMessageBox.warning(self, "خطأ", f"حدث خطأ في تحميل المدارس:\n{str(e)}")
    
    def load_student_data(self):
        """تحميل بيانات الطالب الحالية"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT first_name, first_name_en, last_name, last_name_en,
                       birth_date, gender, national_id, school_id, grade,
                       section, student_number, enrollment_year, status,
                       guardian_name, guardian_phone, address, photo
                FROM students WHERE id = ?
            """, (self.student_id,))
            
            student = cursor.fetchone()
            conn.close()
            
            if student:
                # ملء الحقول بالبيانات الحالية
                self.first_name_edit.setText(student[0] or "")
                self.first_name_en_edit.setText(student[1] or "")
                self.last_name_edit.setText(student[2] or "")
                self.last_name_en_edit.setText(student[3] or "")
                
                # تاريخ الميلاد
                if student[4]:
                    self.birth_date_edit.setDate(QDate.fromString(student[4], "yyyy-MM-dd"))
                
                # الجنس
                if student[5]:
                    index = self.gender_combo.findText(student[5])
                    if index >= 0:
                        self.gender_combo.setCurrentIndex(index)
                
                self.national_id_edit.setText(student[6] or "")
                
                # المدرسة
                if student[7]:
                    for i in range(self.school_combo.count()):
                        if self.school_combo.itemData(i) == student[7]:
                            self.school_combo.setCurrentIndex(i)
                            break
                
                # الصف
                if student[8]:
                    index = self.grade_combo.findText(student[8])
                    if index >= 0:
                        self.grade_combo.setCurrentIndex(index)
                
                self.section_edit.setText(student[9] or "")
                self.student_number_edit.setText(student[10] or "")
                
                if student[11]:
                    self.enrollment_year_spin.setValue(student[11])
                
                # الحالة
                if student[12]:
                    index = self.status_combo.findText(student[12])
                    if index >= 0:
                        self.status_combo.setCurrentIndex(index)
                
                self.guardian_name_edit.setText(student[13] or "")
                self.guardian_phone_edit.setText(student[14] or "")
                self.address_edit.setPlainText(student[15] or "")
                
                # الصورة
                if student[16]:
                    self.current_photo = student[16]
                    self.load_current_photo()
                    
        except Exception as e:
            logging.error(f"خطأ في تحميل بيانات الطالب: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تحميل البيانات:\n{str(e)}")
    
    def load_current_photo(self):
        """تحميل الصورة الحالية"""
        if self.current_photo:
            photo_path = os.path.join(os.path.dirname(self.db_path), 'photos', 'students', self.current_photo)
            if os.path.exists(photo_path):
                pixmap = QPixmap(photo_path)
                scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_label.setPixmap(scaled_pixmap)
                self.remove_photo_btn.setEnabled(True)
    
    def select_photo(self):
        """اختيار صورة جديدة للطالب"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            "اختيار صورة الطالب",
            "",
            "ملفات الصور (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            # التحقق من حجم الملف (2 ميجابايت كحد أقصى)
            if os.path.getsize(file_path) > 2 * 1024 * 1024:
                QMessageBox.warning(self, "خطأ", "حجم الصورة يجب أن يكون أقل من 2 ميجابايت")
                return
            
            self.photo_path = file_path
            
            # عرض الصورة الجديدة
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(scaled_pixmap)
            
            self.remove_photo_btn.setEnabled(True)
    
    def remove_photo(self):
        """إزالة الصورة"""
        self.photo_path = None
        self.current_photo = None
        self.photo_label.clear()
        self.photo_label.setText("لا توجد صورة")
        self.remove_photo_btn.setEnabled(False)
    
    def validate_inputs(self):
        """التحقق من صحة البيانات المدخلة"""
        errors = []
        
        # التحقق من الحقول المطلوبة
        if not self.first_name_edit.text().strip():
            errors.append("الاسم الأول (عربي) مطلوب")
            
        if not self.last_name_edit.text().strip():
            errors.append("الاسم الأخير (عربي) مطلوب")
            
        if not self.national_id_edit.text().strip():
            errors.append("رقم الهوية مطلوب")
        elif len(self.national_id_edit.text().strip()) < 10:
            errors.append("رقم الهوية يجب أن يكون 10 أرقام على الأقل")
            
        if self.school_combo.currentIndex() == -1:
            errors.append("يجب اختيار المدرسة")
            
        if not self.guardian_name_edit.text().strip():
            errors.append("اسم ولي الأمر مطلوب")
            
        if not self.guardian_phone_edit.text().strip():
            errors.append("هاتف ولي الأمر مطلوب")
        
        # التحقق من تاريخ الميلاد
        birth_date = self.birth_date_edit.date().toPyDate()
        if birth_date >= datetime.now().date():
            errors.append("تاريخ الميلاد يجب أن يكون في الماضي")
        
        return errors
    
    def save_photo(self):
        """حفظ الصورة الجديدة"""
        if not self.photo_path:
            return self.current_photo
            
        try:
            # حذف الصورة القديمة إذا كانت موجودة
            if self.current_photo:
                old_photo_path = os.path.join(os.path.dirname(self.db_path), 'photos', 'students', self.current_photo)
                if os.path.exists(old_photo_path):
                    os.remove(old_photo_path)
            
            # إنشاء مجلد الصور إذا لم يكن موجوداً
            photos_dir = os.path.join(os.path.dirname(self.db_path), 'photos', 'students')
            os.makedirs(photos_dir, exist_ok=True)
            
            # إنشاء اسم فريد للملف الجديد
            file_extension = os.path.splitext(self.photo_path)[1]
            unique_filename = f"student_{self.student_id}_{uuid.uuid4().hex[:8]}{file_extension}"
            destination_path = os.path.join(photos_dir, unique_filename)
            
            # نسخ الملف الجديد
            shutil.copy2(self.photo_path, destination_path)
            return unique_filename
            
        except Exception as e:
            logging.error(f"خطأ في حفظ الصورة: {e}")
            return self.current_photo
    
    def save_student(self):
        """حفظ التعديلات"""
        # التحقق من صحة البيانات
        errors = self.validate_inputs()
        if errors:
            QMessageBox.warning(self, "خطأ في البيانات", "\n".join(errors))
            return
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # التحقق من عدم تكرار رقم الهوية (باستثناء الطالب الحالي)
            cursor.execute("SELECT id FROM students WHERE national_id = ? AND id != ?", 
                         (self.national_id_edit.text().strip(), self.student_id))
            if cursor.fetchone():
                QMessageBox.warning(self, "خطأ", "رقم الهوية موجود مسبقاً لطالب آخر")
                conn.close()
                return
            
            # معالجة الصورة
            photo_filename = self.save_photo()
            if not photo_filename and not self.current_photo:
                photo_filename = None
            
            # تحديث البيانات
            update_query = """
                UPDATE students SET
                    first_name = ?, first_name_en = ?, last_name = ?, last_name_en = ?,
                    birth_date = ?, gender = ?, national_id = ?, school_id = ?, grade = ?,
                    section = ?, student_number = ?, enrollment_year = ?, status = ?,
                    guardian_name = ?, guardian_phone = ?, address = ?, photo = ?,
                    updated_at = ?
                WHERE id = ?
            """
            
            student_data = (
                self.first_name_edit.text().strip(),
                self.first_name_en_edit.text().strip(),
                self.last_name_edit.text().strip(),
                self.last_name_en_edit.text().strip(),
                self.birth_date_edit.date().toString("yyyy-MM-dd"),
                self.gender_combo.currentText(),
                self.national_id_edit.text().strip(),
                self.school_combo.currentData(),
                self.grade_combo.currentText(),
                self.section_edit.text().strip(),
                self.student_number_edit.text().strip(),
                self.enrollment_year_spin.value(),
                self.status_combo.currentText(),
                self.guardian_name_edit.text().strip(),
                self.guardian_phone_edit.text().strip(),
                self.address_edit.toPlainText().strip(),
                photo_filename,
                datetime.now().isoformat(),
                self.student_id
            )
            
            cursor.execute(update_query, student_data)
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "نجح", "تم تحديث بيانات الطالب بنجاح!")
            self.student_updated.emit()
            self.accept()
            
        except Exception as e:
            logging.error(f"خطأ في حفظ التعديلات: {e}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في حفظ التعديلات:\n{str(e)}")

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    # تطبيق الخط العربي
    font = QFont("Arial", 10)
    app.setFont(font)
    
    # لاختبار النافذة (يحتاج ID طالب موجود)
    dialog = EditStudentDialog(1)
    dialog.show()
    
    sys.exit(app.exec_())
