from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt
from models import Teacher

class TeacherManagerDialog(QDialog):
    """
    教师管理对话框
    """
    
    def __init__(self, parent=None):
        """
        初始化教师管理对话框
        """
        super().__init__(parent)
        self.current_teacher = None
        self.init_ui()
        self.load_teachers()
    
    def init_ui(self):
        """
        初始化UI界面
        """
        self.setWindowTitle('教师管理')
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 搜索区域
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('搜索:'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入姓名或课程类型搜索...')
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton('搜索')
        search_btn.clicked.connect(self.search_teachers)
        search_layout.addWidget(search_btn)
        
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.load_teachers)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # 教师列表
        self.teacher_table = QTableWidget()
        self.teacher_table.setColumnCount(3)
        self.teacher_table.setHorizontalHeaderLabels(['姓名', '联系方式', '可教授课程'])
        self.teacher_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.teacher_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.teacher_table.setSelectionMode(QTableWidget.SingleSelection)
        self.teacher_table.doubleClicked.connect(self.edit_teacher)
        layout.addWidget(self.teacher_table)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton('添加教师')
        add_btn.clicked.connect(self.add_teacher)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton('编辑教师')
        edit_btn.clicked.connect(self.edit_teacher)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton('删除教师')
        delete_btn.clicked.connect(self.delete_teacher)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_teachers(self):
        """
        加载所有教师
        """
        teachers = Teacher.get_all()
        self.update_table(teachers)
    
    def search_teachers(self):
        """
        搜索教师
        """
        keyword = self.search_input.text().strip()
        if not keyword:
            self.load_teachers()
            return
        
        # 尝试按姓名搜索
        teachers = Teacher.search_by_name(keyword)
        if not teachers:
            # 如果没有结果，尝试按课程类型搜索
            teachers = Teacher.get_teachers_by_subject(keyword)
        
        self.update_table(teachers)
    
    def update_table(self, teachers):
        """
        更新表格显示
        """
        self.teacher_table.setRowCount(len(teachers))
        for row, teacher in enumerate(teachers):
            self.teacher_table.setItem(row, 0, QTableWidgetItem(teacher.name))
            self.teacher_table.setItem(row, 1, QTableWidgetItem(teacher.contact))
            self.teacher_table.setItem(row, 2, QTableWidgetItem(teacher.subject_types))
    
    def add_teacher(self):
        """
        添加教师
        """
        dialog = TeacherEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_teachers()
    
    def edit_teacher(self):
        """
        编辑教师
        """
        selected = self.teacher_table.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一个教师')
            return
        
        row = selected[0].row()
        teacher_name = self.teacher_table.item(row, 0).text()
        teachers = Teacher.search_by_name(teacher_name)
        
        if teachers:
            dialog = TeacherEditDialog(self, teachers[0])
            if dialog.exec_() == QDialog.Accepted:
                self.load_teachers()
    
    def delete_teacher(self):
        """
        删除教师
        """
        selected = self.teacher_table.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一个教师')
            return
        
        row = selected[0].row()
        teacher_name = self.teacher_table.item(row, 0).text()
        
        reply = QMessageBox.question(self, '确认删除', 
                                    f'确定要删除教师 "{teacher_name}" 吗？',
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            teachers = Teacher.search_by_name(teacher_name)
            if teachers:
                teachers[0].delete()
                self.load_teachers()

class TeacherEditDialog(QDialog):
    """
    教师编辑对话框
    """
    
    def __init__(self, parent=None, teacher=None):
        """
        初始化教师编辑对话框
        """
        super().__init__(parent)
        self.teacher = teacher
        self.init_ui()
    
    def init_ui(self):
        """
        初始化UI界面
        """
        self.setWindowTitle('编辑教师' if self.teacher else '添加教师')
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 姓名
        layout.addWidget(QLabel('姓名:'))
        self.name_input = QLineEdit()
        if self.teacher:
            self.name_input.setText(self.teacher.name)
        layout.addWidget(self.name_input)
        
        # 联系方式
        layout.addWidget(QLabel('联系方式:'))
        self.contact_input = QLineEdit()
        if self.teacher:
            self.contact_input.setText(self.teacher.contact)
        layout.addWidget(self.contact_input)
        
        # 可教授课程
        layout.addWidget(QLabel('可教授课程 (多个用逗号分隔):'))
        self.subjects_input = QLineEdit()
        if self.teacher:
            self.subjects_input.setText(self.teacher.subject_types)
        layout.addWidget(self.subjects_input)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_teacher)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def save_teacher(self):
        """
        保存教师信息
        """
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, '提示', '姓名不能为空')
            return
        
        if self.teacher:
            # 更新现有教师
            self.teacher.name = name
            self.teacher.contact = self.contact_input.text().strip()
            self.teacher.subject_types = self.subjects_input.text().strip()
            self.teacher.save()
        else:
            # 创建新教师
            teacher = Teacher(
                name=name,
                contact=self.contact_input.text().strip(),
                subject_types=self.subjects_input.text().strip()
            )
            teacher.save()
        
        self.accept()