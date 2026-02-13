from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QMessageBox, QComboBox, QFileDialog)
from PyQt5.QtCore import Qt
from models import Student

class StudentManagerDialog(QDialog):
    """
    学生管理对话框
    """
    
    def __init__(self, parent=None):
        """
        初始化学生管理对话框
        """
        super().__init__(parent)
        self.current_student = None
        self.init_ui()
        self.load_students()
    
    def init_ui(self):
        """
        初始化UI界面
        """
        self.setWindowTitle('学生管理')
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 搜索区域
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('搜索:'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入姓名或标签搜索...')
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton('搜索')
        search_btn.clicked.connect(self.search_students)
        search_layout.addWidget(search_btn)
        
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.load_students)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # 学生列表
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(3)
        self.student_table.setHorizontalHeaderLabels(['姓名', '联系方式', '标签'])
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.student_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.student_table.setSelectionMode(QTableWidget.SingleSelection)
        self.student_table.doubleClicked.connect(self.edit_student)
        layout.addWidget(self.student_table)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton('添加学生')
        add_btn.clicked.connect(self.add_student)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton('编辑学生')
        edit_btn.clicked.connect(self.edit_student)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton('删除学生')
        delete_btn.clicked.connect(self.delete_student)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_students(self):
        """
        加载所有学生
        """
        students = Student.get_all()
        self.update_table(students)
    
    def search_students(self):
        """
        搜索学生
        """
        keyword = self.search_input.text().strip()
        if not keyword:
            self.load_students()
            return
        
        # 尝试按姓名搜索
        students = Student.search_by_name(keyword)
        if not students:
            # 如果没有结果，尝试按标签搜索
            students = Student.search_by_tag(keyword)
        
        self.update_table(students)
    
    def update_table(self, students):
        """
        更新表格显示
        """
        self.student_table.setRowCount(len(students))
        for row, student in enumerate(students):
            self.student_table.setItem(row, 0, QTableWidgetItem(student.name))
            self.student_table.setItem(row, 1, QTableWidgetItem(student.contact))
            self.student_table.setItem(row, 2, QTableWidgetItem(student.tags))
    
    def add_student(self):
        """
        添加学生
        """
        dialog = StudentEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_students()
    
    def edit_student(self):
        """
        编辑学生
        """
        selected = self.student_table.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一个学生')
            return
        
        row = selected[0].row()
        student_name = self.student_table.item(row, 0).text()
        students = Student.search_by_name(student_name)
        
        if students:
            dialog = StudentEditDialog(self, students[0])
            if dialog.exec_() == QDialog.Accepted:
                self.load_students()
    
    def delete_student(self):
        """
        删除学生
        """
        selected = self.student_table.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一个学生')
            return
        
        row = selected[0].row()
        student_name = self.student_table.item(row, 0).text()
        
        reply = QMessageBox.question(self, '确认删除', 
                                    f'确定要删除学生 "{student_name}" 吗？',
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            students = Student.search_by_name(student_name)
            if students:
                students[0].delete()
                self.load_students()

class StudentEditDialog(QDialog):
    """
    学生编辑对话框
    """
    
    def __init__(self, parent=None, student=None):
        """
        初始化学生编辑对话框
        """
        super().__init__(parent)
        self.student = student
        self.init_ui()
    
    def init_ui(self):
        """
        初始化UI界面
        """
        self.setWindowTitle('编辑学生' if self.student else '添加学生')
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 姓名
        layout.addWidget(QLabel('姓名:'))
        self.name_input = QLineEdit()
        if self.student:
            self.name_input.setText(self.student.name)
        layout.addWidget(self.name_input)
        
        # 联系方式
        layout.addWidget(QLabel('联系方式:'))
        self.contact_input = QLineEdit()
        if self.student:
            self.contact_input.setText(self.student.contact)
        layout.addWidget(self.contact_input)
        
        # 标签
        layout.addWidget(QLabel('标签 (多个用逗号分隔):'))
        self.tags_input = QLineEdit()
        if self.student:
            self.tags_input.setText(self.student.tags)
        layout.addWidget(self.tags_input)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_student)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def save_student(self):
        """
        保存学生信息
        """
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, '提示', '姓名不能为空')
            return
        
        if self.student:
            # 更新现有学生
            self.student.name = name
            self.student.contact = self.contact_input.text().strip()
            self.student.tags = self.tags_input.text().strip()
            self.student.save()
        else:
            # 创建新学生
            student = Student(
                name=name,
                contact=self.contact_input.text().strip(),
                tags=self.tags_input.text().strip()
            )
            student.save()
        
        self.accept()