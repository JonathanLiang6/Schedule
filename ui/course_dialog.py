from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QMessageBox, QComboBox, QDateTimeEdit)
from PyQt5.QtCore import Qt, QDateTime
from models import Course, Teacher, Student

class CourseManagerDialog(QDialog):
    """
    课程管理对话框
    """
    
    def __init__(self, parent=None):
        """
        初始化课程管理对话框
        """
        super().__init__(parent)
        self.current_course = None
        self.init_ui()
        self.load_courses()
    
    def init_ui(self):
        """
        初始化UI界面
        """
        self.setWindowTitle('课程管理')
        self.resize(1000, 600)
        
        layout = QVBoxLayout(self)
        
        # 搜索区域
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('搜索:'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入课程名称搜索...')
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton('搜索')
        search_btn.clicked.connect(self.search_courses)
        search_layout.addWidget(search_btn)
        
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.load_courses)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # 课程列表
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(5)
        self.course_table.setHorizontalHeaderLabels(['课程名称', '教师', '班级', '开始时间', '结束时间'])
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.course_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.course_table.setSelectionMode(QTableWidget.SingleSelection)
        self.course_table.doubleClicked.connect(self.edit_course)
        layout.addWidget(self.course_table)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton('添加课程')
        add_btn.clicked.connect(self.add_course)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton('编辑课程')
        edit_btn.clicked.connect(self.edit_course)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton('删除课程')
        delete_btn.clicked.connect(self.delete_course)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_courses(self):
        """
        加载所有课程
        """
        courses = Course.get_all()
        self.update_table(courses)
    
    def search_courses(self):
        """
        搜索课程
        """
        keyword = self.search_input.text().strip()
        if not keyword:
            self.load_courses()
            return
        
        courses = Course.get_all()
        filtered_courses = [c for c in courses if keyword.lower() in c.name.lower()]
        self.update_table(filtered_courses)
    
    def update_table(self, courses):
        """
        更新表格显示
        """
        self.course_table.setRowCount(len(courses))
        for row, course in enumerate(courses):
            self.course_table.setItem(row, 0, QTableWidgetItem(course.name))
            self.course_table.setItem(row, 1, QTableWidgetItem(course.get_teacher_name()))
            self.course_table.setItem(row, 2, QTableWidgetItem(course.class_name))
            self.course_table.setItem(row, 3, QTableWidgetItem(course.start_time))
            self.course_table.setItem(row, 4, QTableWidgetItem(course.end_time))
    
    def add_course(self):
        """
        添加课程
        """
        dialog = CourseEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_courses()
    
    def edit_course(self):
        """
        编辑课程
        """
        selected = self.course_table.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一个课程')
            return
        
        row = selected[0].row()
        course_name = self.course_table.item(row, 0).text()
        courses = Course.get_all()
        matching_courses = [c for c in courses if c.name == course_name]
        
        if matching_courses:
            dialog = CourseEditDialog(self, matching_courses[0])
            if dialog.exec_() == QDialog.Accepted:
                self.load_courses()
    
    def delete_course(self):
        """
        删除课程
        """
        selected = self.course_table.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一个课程')
            return
        
        row = selected[0].row()
        course_name = self.course_table.item(row, 0).text()
        
        reply = QMessageBox.question(self, '确认删除', 
                                    f'确定要删除课程 "{course_name}" 吗？',
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            courses = Course.get_all()
            matching_courses = [c for c in courses if c.name == course_name]
            if matching_courses:
                matching_courses[0].delete()
                self.load_courses()

class CourseEditDialog(QDialog):
    """
    课程编辑对话框
    """
    
    def __init__(self, parent=None, course=None):
        """
        初始化课程编辑对话框
        """
        super().__init__(parent)
        self.course = course
        self.init_ui()
        self.load_teachers()
        self.load_students()
    
    def init_ui(self):
        """
        初始化UI界面
        """
        self.setWindowTitle('编辑课程' if self.course else '添加课程')
        self.resize(500, 400)
        
        layout = QVBoxLayout(self)
        
        # 课程名称
        layout.addWidget(QLabel('课程名称:'))
        self.name_input = QLineEdit()
        if self.course:
            self.name_input.setText(self.course.name)
        layout.addWidget(self.name_input)
        
        # 教师
        layout.addWidget(QLabel('授课教师:'))
        self.teacher_combo = QComboBox()
        layout.addWidget(self.teacher_combo)
        
        # 班级名称
        layout.addWidget(QLabel('班级名称:'))
        self.class_input = QLineEdit()
        if self.course:
            self.class_input.setText(self.course.class_name)
        layout.addWidget(self.class_input)
        
        # 课程类型
        layout.addWidget(QLabel('课程类型:'))
        self.type_input = QLineEdit()
        if self.course:
            self.type_input.setText(self.course.course_type)
        layout.addWidget(self.type_input)
        
        # 开始时间
        layout.addWidget(QLabel('开始时间:'))
        self.start_time_edit = QDateTimeEdit()
        self.start_time_edit.setDisplayFormat('yyyy-MM-dd HH:mm')
        self.start_time_edit.setCalendarPopup(True)
        if self.course:
            self.start_time_edit.setDateTime(QDateTime.fromString(self.course.start_time, 'yyyy-MM-dd HH:mm'))
        layout.addWidget(self.start_time_edit)
        
        # 结束时间
        layout.addWidget(QLabel('结束时间:'))
        self.end_time_edit = QDateTimeEdit()
        self.end_time_edit.setDisplayFormat('yyyy-MM-dd HH:mm')
        self.end_time_edit.setCalendarPopup(True)
        if self.course:
            self.end_time_edit.setDateTime(QDateTime.fromString(self.course.end_time, 'yyyy-MM-dd HH:mm'))
        layout.addWidget(self.end_time_edit)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_course)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def load_teachers(self):
        """
        加载教师列表
        """
        teachers = Teacher.get_all()
        self.teacher_combo.clear()
        self.teacher_combo.addItem('请选择教师', None)
        for teacher in teachers:
            self.teacher_combo.addItem(teacher.name, teacher.id)
        
        if self.course and self.course.teacher_id:
            index = self.teacher_combo.findData(self.course.teacher_id)
            if index >= 0:
                self.teacher_combo.setCurrentIndex(index)
    
    def load_students(self):
        """
        加载学生列表
        """
        pass
    
    def save_course(self):
        """
        保存课程信息
        """
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, '提示', '课程名称不能为空')
            return
        
        teacher_id = self.teacher_combo.currentData()
        if not teacher_id:
            QMessageBox.warning(self, '提示', '请选择授课教师')
            return
        
        start_time = self.start_time_edit.dateTime().toString('yyyy-MM-dd HH:mm')
        end_time = self.end_time_edit.dateTime().toString('yyyy-MM-dd HH:mm')
        
        if start_time >= end_time:
            QMessageBox.warning(self, '提示', '结束时间必须大于开始时间')
            return
        
        if self.course:
            # 更新现有课程
            self.course.name = name
            self.course.teacher_id = teacher_id
            self.course.class_name = self.class_input.text().strip()
            self.course.course_type = self.type_input.text().strip()
            self.course.start_time = start_time
            self.course.end_time = end_time
            try:
                self.course.save()
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, '错误', str(e))
        else:
            # 创建新课程
            course = Course(
                name=name,
                teacher_id=teacher_id,
                class_name=self.class_input.text().strip(),
                course_type=self.type_input.text().strip(),
                start_time=start_time,
                end_time=end_time
            )
            try:
                course.save()
                self.accept()
            except Exception as e:
                QMessageBox.warning(self, '错误', str(e))