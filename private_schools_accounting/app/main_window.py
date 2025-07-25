#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
النافذة الرئيسية لتطبيق حسابات المدارس الأهلية
"""

import logging
import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QFrame, QLabel, QPushButton, 
    QMessageBox, QMenuBar, QStatusBar, QAction,
    QSplitter, QScrollArea
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPixmap, QKeySequence

import config
from core.auth.login_manager import auth_manager
from core.utils.logger import log_user_action


class MainWindow(QMainWindow):
    """النافذة الرئيسية للتطبيق"""
    
    # إشارات مخصصة
    page_changed = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_page = None
        self.pages = {}
        self.sidebar_buttons = {}
        
        self.setup_window()
        self.create_ui()
        self.setup_styles()
        self.setup_menu_bar()
        self.setup_status_bar()
        self.setup_session_timer()
        
        # عرض الصفحة الرئيسية
        self.show_dashboard()
        
        log_user_action("تم فتح النافذة الرئيسية")
    
    def setup_window(self):
        """إعداد النافذة الرئيسية"""
        try:
            # عنوان النافذة
            self.setWindowTitle(config.WINDOW_TITLE)
            
            # حجم النافذة
            self.setMinimumSize(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT)
            self.resize(1400, 900)
            
            # توسيط النافذة
            self.center_window()
            
            # اتجاه التخطيط
            self.setLayoutDirection(Qt.RightToLeft)
            
            # أيقونة النافذة
            self.setup_window_icon()
            
        except Exception as e:
            logging.error(f"خطأ في إعداد النافذة الرئيسية: {e}")
            raise
    
    def center_window(self):
        """توسيط النافذة في الشاشة"""
        try:
            from PyQt5.QtWidgets import QDesktopWidget
            
            screen = QDesktopWidget().screenGeometry()
            window = self.geometry()
            
            x = (screen.width() - window.width()) // 2
            y = (screen.height() - window.height()) // 2
            
            self.move(x, y)
            
        except Exception as e:
            logging.error(f"خطأ في توسيط النافذة: {e}")
    
    def setup_window_icon(self):
        """إعداد أيقونة النافذة"""
        try:
            icon_path = config.RESOURCES_DIR / "images" / "icons" / "logo.png"
            if icon_path.exists():
                self.setWindowIcon(QIcon(str(icon_path)))
        except Exception as e:
            logging.warning(f"تحذير: لم يتم تحميل أيقونة النافذة: {e}")
    
    def create_ui(self):
        """إنشاء واجهة المستخدم"""
        try:
            # الويدجت المركزي
            central_widget = QWidget()
            self.setCentralWidget(central_widget)
            
            # التخطيط الرئيسي
            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)
            
            # إنشاء القائمة الجانبية
            self.create_sidebar()
            
            # إنشاء منطقة المحتوى
            self.create_content_area()
            
            # إضافة المكونات للتخطيط (نص إلى اليمين)
            main_layout.addWidget(self.sidebar_frame)
            main_layout.addWidget(self.content_frame, 1)  # تمديد منطقة المحتوى
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء واجهة المستخدم: {e}")
            raise
    
    def create_sidebar(self):
        """إنشاء القائمة الجانبية"""
        try:
            # إطار القائمة الجانبية
            self.sidebar_frame = QFrame()
            self.sidebar_frame.setObjectName("sidebarFrame")
            self.sidebar_frame.setFixedWidth(300)  # زيادة العرض قليلاً
            
            sidebar_layout = QVBoxLayout(self.sidebar_frame)
            sidebar_layout.setContentsMargins(0, 0, 0, 0)
            sidebar_layout.setSpacing(0)
            
            # رأس القائمة الجانبية
            self.create_sidebar_header(sidebar_layout)
            
            # منطقة التمرير للأزرار
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setObjectName("sidebarScrollArea")
            
            # ويدجت الأزرار
            buttons_widget = QWidget()
            buttons_layout = QVBoxLayout(buttons_widget)
            buttons_layout.setContentsMargins(0, 10, 0, 10)
            buttons_layout.setSpacing(8)  # زيادة التباعد بين الأزرار
            
            # إنشاء أزرار القائمة
            self.create_sidebar_buttons(buttons_layout)
            
            # إضافة مساحة مرنة في النهاية
            buttons_layout.addStretch()
            
            scroll_area.setWidget(buttons_widget)
            sidebar_layout.addWidget(scroll_area)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء القائمة الجانبية: {e}")
            raise
    
    def create_sidebar_header(self, layout):
        """إنشاء رأس القائمة الجانبية"""
        try:
            # إطار الرأس
            header_frame = QFrame()
            header_frame.setObjectName("sidebarHeader")
            header_frame.setFixedHeight(10)
            
            header_layout = QVBoxLayout(header_frame)
            header_layout.setAlignment(Qt.AlignCenter)
            header_layout.setContentsMargins(20, 15, 20, 15)
            
            # عنوان التطبيق
            title_label = QLabel("حسابات المدارس")
            title_label.setObjectName("appTitle")
            title_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(title_label)
            
            # نسخة التطبيق
            version_label = QLabel(f"الإصدار {config.APP_VERSION}")
            version_label.setObjectName("appVersion")
            version_label.setAlignment(Qt.AlignCenter)
            header_layout.addWidget(version_label)
            
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء رأس القائمة الجانبية: {e}")
            raise
    
    def create_sidebar_buttons(self, layout):
        """إنشاء أزرار القائمة الجانبية"""
        try:
            # تعريف أزرار القائمة
            menu_items = [
                {"name": "dashboard", "text": "الرئيسية", "icon": "dashboard.png", "active": True},
                {"name": "schools", "text": "المدارس", "icon": "schools.png", "active": True},
                {"name": "students", "text": "الطلاب", "icon": "students.png", "active": True},
                {"name": "installments", "text": "الأقساط", "icon": "installments.png", "active": True},
                {"name": "additional_fees", "text": "الرسوم الإضافية", "icon": "fees.png", "active": True},
                {"name": "separator1", "text": "---", "icon": None, "active": False},
                {"name": "external_income", "text": "الواردات الخارجية", "icon": "income.png", "active": True},
                {"name": "expenses", "text": "المصروفات", "icon": "expenses.png", "active": True},
                {"name": "separator2", "text": "---", "icon": None, "active": False},
                {"name": "reports", "text": "التقارير", "icon": "reports.png", "active": False},
                {"name": "salaries", "text": "الرواتب", "icon": "salaries.png", "active": False},
                {"name": "separator2", "text": "---", "icon": None, "active": False},
                {"name": "settings", "text": "الإعدادات", "icon": "settings.png", "active": False},
                {"name": "logout", "text": "تسجيل خروج", "icon": "logout.png", "active": True},
            ]
            
            for item in menu_items:
                if item["text"] == "---":
                    # إضافة فاصل
                    separator = QFrame()
                    separator.setFrameShape(QFrame.HLine)
                    separator.setObjectName("menuSeparator")
                    layout.addWidget(separator)
                else:
                    # إنشاء زر القائمة
                    button = self.create_menu_button(
                        item["name"], 
                        item["text"], 
                        item["icon"], 
                        item["active"]
                    )
                    self.sidebar_buttons[item["name"]] = button
                    layout.addWidget(button)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء أزرار القائمة الجانبية: {e}")
            raise
    
    def create_menu_button(self, name: str, text: str, icon: str, active: bool):
        """إنشاء زر القائمة"""
        try:
            button = QPushButton(text)
            button.setObjectName("menuButton")
            button.setCheckable(True)
            button.setFixedHeight(55)  # زيادة الارتفاع
            
            # إضافة خصائص للزر
            button.setProperty("page_name", name)
            button.setProperty("active", active)
            
            # تحسين محاذاة النص إلى اليمين
            button.setLayoutDirection(Qt.RightToLeft)
            button.setStyleSheet("text-align: right; padding-right: 25px;")
            
            # ربط الإشارة
            if name == "logout":
                button.clicked.connect(self.logout)
            elif active:
                button.clicked.connect(lambda: self.navigate_to_page(name))
            else:
                button.clicked.connect(self.show_coming_soon)
                button.setProperty("coming_soon", True)
            
            return button
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء زر القائمة {name}: {e}")
            return QPushButton(text)
    
    def create_content_area(self):
        """إنشاء منطقة المحتوى"""
        try:
            # إطار المحتوى
            self.content_frame = QFrame()
            self.content_frame.setObjectName("contentFrame")
            
            content_layout = QVBoxLayout(self.content_frame)
            content_layout.setContentsMargins(20, 20, 20, 20)
            content_layout.setSpacing(0)
            
            # شريط العنوان
            self.create_content_header(content_layout)
            
            # منطقة الصفحات
            self.pages_stack = QStackedWidget()
            self.pages_stack.setObjectName("pagesStack")
            content_layout.addWidget(self.pages_stack)
            
            # تحميل الصفحات
            self.load_pages()
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء منطقة المحتوى: {e}")
            raise
    
    def create_content_header(self, layout):
        """إنشاء شريط عنوان المحتوى"""
        try:
            # إطار شريط العنوان
            header_frame = QFrame()
            header_frame.setObjectName("contentHeader")
            header_frame.setFixedHeight(60)
            
            header_layout = QHBoxLayout(header_frame)
            header_layout.setContentsMargins(20, 5, 20, 5) # Reduced vertical margins
            header_layout.setAlignment(Qt.AlignVCenter) # Align content vertically in the center
            
            # عنوان الصفحة
            self.page_title = QLabel("لوحة التحكم")
            self.page_title.setObjectName("pageTitle")
            header_layout.addWidget(self.page_title)
            
            # مساحة مرنة
            header_layout.addStretch()
            
            layout.addWidget(header_frame)
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء شريط عنوان المحتوى: {e}")
            raise
    
    def create_user_info(self):
        """إنشاء معلومات المستخدم"""
        try:
            user_frame = QFrame()
            user_frame.setObjectName("userInfo")
            
            user_layout = QHBoxLayout(user_frame)
            user_layout.setContentsMargins(15, 8, 15, 8)
            
            return user_frame
            
        except Exception as e:
            logging.error(f"خطأ في إنشاء معلومات المستخدم: {e}")
            return QFrame()
    
    def load_pages(self):
        """تحميل صفحات التطبيق"""
        try:
            # صفحة لوحة التحكم
            self.load_dashboard_page()
            
            # صفحة المدارس
            self.load_schools_page()
            
            # صفحة الطلاب
            self.load_students_page()
            
            # صفحة الأقساط
            self.load_installments_page()
            
            # صفحة الرسوم الإضافية
            self.load_additional_fees_page()
            
            # صفحة الواردات الخارجية
            self.load_external_income_page()
            
            # صفحة المصروفات
            self.load_expenses_page()
            
            # الصفحات الشكلية
            self.load_placeholder_pages()
            
        except Exception as e:
            logging.error(f"خطأ في تحميل الصفحات: {e}")
            raise
    
    def load_dashboard_page(self):
        """تحميل صفحة لوحة التحكم"""
        try:
            from ui.pages.dashboard.dashboard_page import DashboardPage
            
            dashboard = DashboardPage()
            self.pages["dashboard"] = dashboard
            self.pages_stack.addWidget(dashboard)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة لوحة التحكم: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("لوحة التحكم", "مرحباً بك في نظام حسابات المدارس الأهلية")
            self.pages["dashboard"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_schools_page(self):
        """تحميل صفحة المدارس"""
        try:
            from ui.pages.schools.schools_page import SchoolsPage
            
            schools = SchoolsPage()
            self.pages["schools"] = schools
            self.pages_stack.addWidget(schools)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة المدارس: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("المدارس", "صفحة إدارة المدارس")
            self.pages["schools"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_students_page(self):
        """تحميل صفحة الطلاب"""
        try:
            from ui.pages.students.students_page import StudentsPage
            students = StudentsPage()
            self.pages["students"] = students
            self.pages_stack.addWidget(students)
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة الطلاب: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("الطلاب", "صفحة إدارة الطلاب")
            self.pages["students"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_installments_page(self):
        """تحميل صفحة الأقساط"""
        try:
            from ui.pages.installments.installments_page import InstallmentsPage
            
            installments = InstallmentsPage()
            self.pages["installments"] = installments
            self.pages_stack.addWidget(installments)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة الأقساط: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("الأقساط", "صفحة إدارة الأقساط")
            self.pages["installments"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_additional_fees_page(self):
        """تحميل صفحة الرسوم الإضافية"""
        try:
            from ui.pages.additional_fees.additional_fees_page import AdditionalFeesPage
            
            additional_fees = AdditionalFeesPage()
            self.pages["additional_fees"] = additional_fees
            self.pages_stack.addWidget(additional_fees)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة الرسوم الإضافية: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("الرسوم الإضافية", "صفحة إدارة الرسوم الإضافية")
            self.pages["additional_fees"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_external_income_page(self):
        """تحميل صفحة الواردات الخارجية"""
        try:
            from ui.pages.external_income.external_income_page import ExternalIncomePage
            
            external_income = ExternalIncomePage()
            self.pages["external_income"] = external_income
            self.pages_stack.addWidget(external_income)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة الواردات الخارجية: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("الواردات الخارجية", "صفحة إدارة الواردات الخارجية")
            self.pages["external_income"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_expenses_page(self):
        """تحميل صفحة المصروفات"""
        try:
            from ui.pages.expenses.expenses_page import ExpensesPage
            
            expenses = ExpensesPage()
            self.pages["expenses"] = expenses
            self.pages_stack.addWidget(expenses)
            
        except Exception as e:
            logging.error(f"خطأ في تحميل صفحة المصروفات: {e}")
            # إنشاء صفحة بديلة
            placeholder = self.create_placeholder_page("المصروفات", "صفحة إدارة المصروفات")
            self.pages["expenses"] = placeholder
            self.pages_stack.addWidget(placeholder)
    
    def load_placeholder_pages(self):
        """تحميل الصفحات الشكلية"""
        try:
            placeholder_pages = [
                ("reports", "التقارير"),
                ("salaries", "الرواتب"),
                ("settings", "الإعدادات")
            ]
            
            for page_name, page_title in placeholder_pages:
                placeholder = self.create_placeholder_page(
                    page_title, 
                    f"صفحة {page_title} قيد التطوير..."
                )
                self.pages[page_name] = placeholder
                self.pages_stack.addWidget(placeholder)
                
        except Exception as e:
            logging.error(f"خطأ في تحميل الصفحات الشكلية: {e}")
    
    def create_placeholder_page(self, title: str, message: str):
        """إنشاء صفحة بديلة"""
        try:
            widget = QWidget()
            layout = QVBoxLayout(widget)
            layout.setAlignment(Qt.AlignCenter)

            # رسالة
            label = QLabel(message)
            label.setAlignment(Qt.AlignCenter)
            label.setObjectName("placeholderMessage")
            layout.addWidget(label)

            return widget

        except Exception as e:
            logging.error(f"خطأ في إنشاء الصفحة البديلة: {e}")
            return QWidget()
    
    def navigate_to_page(self, page_name: str):
        """الانتقال إلى صفحة معينة"""
        try:
            if page_name not in self.pages:
                logging.warning(f"الصفحة غير موجودة: {page_name}")
                return

            # تحديث حالة الأزرار
            self.update_sidebar_buttons(page_name)

            # عرض الصفحة
            page_widget = self.pages[page_name]
            self.pages_stack.setCurrentWidget(page_widget)

            # تحديث عنوان الصفحة
            self.update_page_title(page_name)

            # تحديث الصفحة الحالية
            self.current_page = page_name

            # إرسال إشارة تغيير الصفحة
            self.page_changed.emit(page_name)

            # تسجيل الإجراء
            log_user_action("تم الانتقال إلى صفحة", page_name)

        except Exception as e:
            logging.error(f"خطأ في الانتقال إلى الصفحة {page_name}: {e}")
    
    def update_sidebar_buttons(self, active_page: str):
        """تحديث حالة أزرار القائمة الجانبية"""
        try:
            for page_name, button in self.sidebar_buttons.items():
                button.setChecked(page_name == active_page)
                
        except Exception as e:
            logging.error(f"خطأ في تحديث أزرار القائمة الجانبية: {e}")
    
    def update_page_title(self, page_name: str):
        """تحديث عنوان الصفحة"""
        try:
            titles = {
                "dashboard": "لوحة التحكم",
                "schools": "المدارس",
                "students": "الطلاب",
                "installments": "الأقساط",
                "additional_fees": "الرسوم الإضافية",
                "reports": "التقارير",
                "external_income": "الواردات الخارجية",
                "expenses": "المصروفات",
                "salaries": "الرواتب",
                "settings": "الإعدادات"
            }
            
            title = titles.get(page_name, "غير معروف")
            self.page_title.setText(title)
            
        except Exception as e:
            logging.error(f"خطأ في تحديث عنوان الصفحة: {e}")
    
    def show_dashboard(self):
        """عرض صفحة لوحة التحكم"""
        self.navigate_to_page("dashboard")
    def show_coming_soon(self):
        """عرض رسالة قريباً"""
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("قريباً")
            msg.setText("هذه الميزة قيد التطوير وستكون متاحة قريباً")
            msg.setLayoutDirection(Qt.RightToLeft)
            msg.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة قريباً: {e}")
    
    def setup_menu_bar(self):
        """إعداد شريط القوائم"""
        try:
            menubar = self.menuBar()
            menubar.setLayoutDirection(Qt.RightToLeft)
            
            # قائمة ملف
            file_menu = menubar.addMenu("ملف")
            
            # خروج
            exit_action = QAction("خروج", self)
            exit_action.setShortcut(QKeySequence.Quit)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)
            
            # قائمة عرض
            view_menu = menubar.addMenu("عرض")
            
            # تحديث
            refresh_action = QAction("تحديث", self)
            refresh_action.setShortcut(QKeySequence.Refresh)
            refresh_action.triggered.connect(self.refresh_current_page)
            view_menu.addAction(refresh_action)
            
            # قائمة مساعدة
            help_menu = menubar.addMenu("مساعدة")
            
            # حول
            about_action = QAction("حول التطبيق", self)
            about_action.triggered.connect(self.show_about)
            help_menu.addAction(about_action)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد شريط القوائم: {e}")
    
    def setup_status_bar(self):
        """إعداد شريط الحالة"""
        try:
            statusbar = self.statusBar()
            statusbar.setLayoutDirection(Qt.RightToLeft)
            
            # رسالة الحالة
            statusbar.showMessage("جاهز")
            
            # معلومات إضافية (يمكن إضافتها لاحقاً)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد شريط الحالة: {e}")
    
    def setup_session_timer(self):
        """إعداد مؤقت الجلسة"""
        try:
            # مؤقت للتحقق من انتهاء الجلسة
            self.session_timer = QTimer()
            self.session_timer.timeout.connect(self.check_session)
            self.session_timer.start(60000)  # كل دقيقة
            
        except Exception as e:
            logging.error(f"خطأ في إعداد مؤقت الجلسة: {e}")
    
    def check_session(self):
        """التحقق من حالة الجلسة"""
        try:
            if not auth_manager.is_authenticated():
                self.show_session_expired()
                
        except Exception as e:
            logging.error(f"خطأ في التحقق من الجلسة: {e}")
    
    def show_session_expired(self):
        """عرض رسالة انتهاء الجلسة"""
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("انتهت الجلسة")
            msg.setText("انتهت جلسة العمل. يرجى تسجيل الدخول مرة أخرى.")
            msg.setLayoutDirection(Qt.RightToLeft)
            msg.finished.connect(self.close)
            msg.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض رسالة انتهاء الجلسة: {e}")
            self.close()
    
    def refresh_current_page(self):
        """تحديث الصفحة الحالية"""
        try:
            if self.current_page and self.current_page in self.pages:
                page_widget = self.pages[self.current_page]
                if hasattr(page_widget, 'refresh'):
                    page_widget.refresh()
                    
                log_user_action("تم تحديث الصفحة", self.current_page)
                
        except Exception as e:
            logging.error(f"خطأ في تحديث الصفحة الحالية: {e}")
    
    def show_about(self):
        """عرض معلومات التطبيق"""
        try:
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("حول التطبيق")
            msg.setText(f"""
                {config.APP_NAME}
                الإصدار: {config.APP_VERSION}
                
                تطبيق محاسبي متكامل لإدارة حسابات المدارس الأهلية
                
                تطوير: {config.APP_ORGANIZATION}
            """)
            msg.setLayoutDirection(Qt.RightToLeft)
            msg.exec_()
            
        except Exception as e:
            logging.error(f"خطأ في عرض معلومات التطبيق: {e}")
    
    def logout(self):
        """تسجيل خروج"""
        try:
            reply = QMessageBox.question(
                self,
                "تسجيل خروج",
                "هل تريد تسجيل الخروج من التطبيق؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                auth_manager.logout()
                log_user_action("تم تسجيل الخروج")
                self.close()
                
        except Exception as e:
            logging.error(f"خطأ في تسجيل الخروج: {e}")
    
    def setup_styles(self):
        """إعداد تنسيقات النافذة"""
        try:
            style = """
                QMainWindow {
                    background-color: #F8F9FA;
                    font-family: 'Segoe UI', Tahoma, Arial;
                }
                
                /* القائمة الجانبية */
                #sidebarFrame {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 1, stop: 0 #2C3E50, stop: 1 #1a2530);
                    border-right: 1px solid #34495E;
                }
                
                #sidebarHeader {
                    background-color: #34495E;
                    border-bottom: 1px solid #2C3E50;
                    padding: 10px;
                }
                
                #appTitle {
                    color: white;
                    font-size: 26px;
                    font-weight: bold;
                    text-align: center;
                }
                
                #appVersion {
                    color: #BDC3C7;
                    font-size: 16px;
                    text-align: center;
                }
                
                #sidebarScrollArea {
                    background-color: transparent;
                    border: none;
                }
                
                #menuButton {
                    background-color: transparent;
                    border: none;
                    color: #BDC3C7;
                    text-align: right;
                    padding: 15px 25px;
                    font-size: 18px;
                    border-radius: 8px;
                    margin: 5px 10px;
                }
                
                #menuButton:hover {
                    background-color: #34495E;
                    color: white;
                }
                
                #menuButton:checked {
                    background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0, stop: 0 #3498DB, stop: 1 #2980B9);
                    color: white;
                    font-weight: bold;
                }
                
                #menuButton[coming_soon="true"] {
                    color: #7F8C8D;
                    font-style: italic;
                }
                
                #menuSeparator {
                    color: #34495E;
                    margin: 10px 20px;
                    height: 1px;
                    background-color: #34495E;
                }
                
                /* منطقة المحتوى */
                #contentFrame {
                    background-color: #F8F9FA;
                }
                
                #contentHeader {
                    background-color: white;
                    border-bottom: 1px solid #E9ECEF;
                    border-radius: 8px 8px 0 0;
                    padding: 5px 20px; /* Reduced vertical padding */
                }
                
                #pageTitle {
                    font-size: 24px;
                    font-weight: bold;
                    color: #2C3E50;
                }
                
                #userInfo {
                    background-color: #ECF0F1;
                    border-radius: 20px;
                    padding: 8px 15px;
                }
                
                #userName {
                    color: #2C3E50;
                    font-size: 16px;
                    font-weight: bold;
                }
                
                #pagesStack {
                    background-color: white;
                    border-radius: 0 0 8px 8px;
                    border: 1px solid #E9ECEF;
                }
                
                #placeholderMessage {
                    font-size: 24px;
                    color: #7F8C8D;
                    padding: 50px;
                }
                
                /* شريط القوائم */
                QMenuBar {
                    background-color: #2C3E50;
                    color: white;
                    border-bottom: 1px solid #34495E;
                }
                
                QMenuBar::item {
                    background-color: transparent;
                    padding: 8px 16px;
                }
                
                QMenuBar::item:selected {
                    background-color: #34495E;
                }
                
                QMenu {
                    background-color: white;
                    border: 1px solid #BDC3C7;
                    color: #2C3E50;
                }
                
                QMenu::item {
                    padding: 8px 16px;
                }
                
                QMenu::item:selected {
                    background-color: #ECF0F1;
                }
                
                /* شريط الحالة */
                QStatusBar {
                    background-color: #ECF0F1;
                    border-top: 1px solid #BDC3C7;
                    color: #2C3E50;
                }
            """
            
            self.setStyleSheet(style)
            
        except Exception as e:
            logging.error(f"خطأ في إعداد التنسيقات: {e}")
    
    def closeEvent(self, event):
        """معالجة إغلاق النافذة"""
        try:
            reply = QMessageBox.question(
                self,
                "إغلاق التطبيق",
                "هل تريد إغلاق التطبيق؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # تنظيف الموارد
                if hasattr(self, 'session_timer'):
                    self.session_timer.stop()
                
                auth_manager.logout()
                log_user_action("تم إغلاق التطبيق")
                event.accept()
            else:
                event.ignore()
                
        except Exception as e:
            logging.error(f"خطأ في إغلاق النافذة: {e}")
            event.accept()
    
    def show_page_widget(self, widget):
        """عرض ويدجت كصفحة مؤقتة"""
        try:
            # إضافة الويدجت للمكدس
            self.pages_stack.addWidget(widget)
            
            # عرض الويدجت
            self.pages_stack.setCurrentWidget(widget)
            
            # تحديث عنوان الصفحة
            if hasattr(widget, 'windowTitle'):
                title = widget.windowTitle()
                if title:
                    self.page_title.setText(title)
                else:
                    self.page_title.setText("تفاصيل الطالب")
            else:
                self.page_title.setText("تفاصيل الطالب")
            
            # إلغاء تفعيل أزرار الشريط الجانبي
            self.update_sidebar_buttons("")
            
        except Exception as e:
            logging.error(f"خطأ في عرض الويدجت: {e}")
    
    def show_students_page(self):
        """العودة لصفحة الطلاب"""
        try:
            self.navigate_to_page("students")
            
        except Exception as e:
            logging.error(f"خطأ في العودة لصفحة الطلاب: {e}")
