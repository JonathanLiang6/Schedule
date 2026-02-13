from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QFileDialog, QMessageBox,
                           QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from models import Student, Teacher, Course, Textbook
from utils.tools import read_csv_file, write_csv_file, validate_student_data, validate_teacher_data, validate_course_data

class ImportExportDialog(QDialog):
    """
    导入导出对话框
    """
    
    def __init__(self, parent=None):
        """
        初始化导入导出对话框
        """
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """
        初始化UI界面
        """
        self.setWindowTitle('导入导出数据')
        self.resize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 类型选择
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel('数据类型:'))
        self.type_combo = QComboBox()
        self.type_combo.addItems(['学生', '教师', '课程', '教材'])
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # 操作选择
        action_layout = QHBoxLayout()
        self.import_btn = QPushButton('导入数据')
        self.import_btn.clicked.connect(self.import_data)
        self.export_btn = QPushButton('导出数据')
        self.export_btn.clicked.connect(self.export_data)
        action_layout.addWidget(self.import_btn)
        action_layout.addWidget(self.export_btn)
        layout.addLayout(action_layout)
        
        # 预览区域
        layout.addWidget(QLabel('数据预览:'))
        self.preview_table = QTableWidget()
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.preview_table)
        
        # 关闭按钮
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
    
    def import_data(self):
        """
        导入数据
        """
        data_type = self.type_combo.currentText()
        
        # 选择文件
        file_path, _ = QFileDialog.getOpenFileName(
            self, 
            f'选择{data_type}数据文件', 
            '', 
            'CSV文件 (*.csv);;所有文件 (*.*)'
        )
        
        if not file_path:
            return
        
        # 读取CSV文件
        data = read_csv_file(file_path)
        if not data:
            QMessageBox.warning(self, '错误', '文件为空或格式错误')
            return
        
        # 验证数据
        is_valid, message = self.validate_data(data_type, data)
        if not is_valid:
            QMessageBox.warning(self, '验证失败', message)
            return
        
        # 显示预览
        self.show_preview(data)
        
        # 确认导入
        reply = QMessageBox.question(
            self, 
            '确认导入', 
            f'确定要导入 {len(data)} 条{data_type}数据吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 执行导入
            success_count = self.perform_import(data_type, data)
            QMessageBox.information(self, '导入完成', f'成功导入 {success_count} 条{data_type}数据')
            self.accept()
    
    def export_data(self):
        """
        导出数据
        """
        data_type = self.type_combo.currentText()
        
        # 获取数据
        data = self.get_export_data(data_type)
        if not data:
            QMessageBox.information(self, '提示', f'没有可导出的{data_type}数据')
            return
        
        # 选择保存路径
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            f'保存{data_type}数据', 
            f'{data_type}.csv', 
            'CSV文件 (*.csv);;所有文件 (*.*)'
        )
        
        if not file_path:
            return
        
        # 获取表头
        headers = self.get_export_headers(data_type)
        
        # 写入CSV文件
        if write_csv_file(file_path, data, headers):
            QMessageBox.information(self, '导出完成', f'成功导出 {len(data)} 条{data_type}数据')
        else:
            QMessageBox.warning(self, '错误', '导出失败')
    
    def validate_data(self, data_type, data):
        """
        验证数据
        """
        if data_type == '学生':
            return validate_student_data(data)
        elif data_type == '教师':
            return validate_teacher_data(data)
        elif data_type == '课程':
            return validate_course_data(data)
        elif data_type == '教材':
            return True, '验证通过'
        return False, '未知的数据类型'
    
    def perform_import(self, data_type, data):
        """
        执行导入
        """
        success_count = 0
        
        for item in data:
            try:
                if data_type == '学生':
                    student = Student(
                        name=item.get('姓名', ''),
                        contact=item.get('联系方式', ''),
                        tags=item.get('标签', '')
                    )
                    student.save()
                    success_count += 1
                
                elif data_type == '教师':
                    teacher = Teacher(
                        name=item.get('姓名', ''),
                        contact=item.get('联系方式', ''),
                        subject_types=item.get('可教授课程类型', '')
                    )
                    teacher.save()
                    success_count += 1
                
                elif data_type == '课程':
                    # 需要先找到教师
                    teacher_name = item.get('教师姓名', '')
                    teachers = Teacher.search_by_name(teacher_name)
                    if teachers:
                        course = Course(
                            name=item.get('课程名称', ''),
                            teacher_id=teachers[0].id,
                            class_name=item.get('班级名称', ''),
                            course_type=item.get('课程类型', ''),
                            start_time=item.get('开始时间', ''),
                            end_time=item.get('结束时间', '')
                        )
                        course.save()
                        success_count += 1
                
                elif data_type == '教材':
                    textbook = Textbook(
                        name=item.get('教材名称', ''),
                        price=float(item.get('价格', 0)),
                        description=item.get('描述', '')
                    )
                    textbook.save()
                    success_count += 1
            
            except Exception as e:
                print(f'导入失败: {e}')
                continue
        
        return success_count
    
    def get_export_data(self, data_type):
        """
        获取导出数据
        """
        data = []
        
        if data_type == '学生':
            students = Student.get_all()
            for student in students:
                data.append({
                    '姓名': student.name,
                    '联系方式': student.contact,
                    '标签': student.tags
                })
        
        elif data_type == '教师':
            teachers = Teacher.get_all()
            for teacher in teachers:
                data.append({
                    '姓名': teacher.name,
                    '联系方式': teacher.contact,
                    '可教授课程类型': teacher.subject_types
                })
        
        elif data_type == '课程':
            courses = Course.get_all()
            for course in courses:
                data.append({
                    '课程名称': course.name,
                    '教师姓名': course.get_teacher_name(),
                    '班级名称': course.class_name,
                    '课程类型': course.course_type,
                    '开始时间': course.start_time,
                    '结束时间': course.end_time
                })
        
        elif data_type == '教材':
            textbooks = Textbook.get_all()
            for textbook in textbooks:
                data.append({
                    '教材名称': textbook.name,
                    '价格': str(textbook.price),
                    '描述': textbook.description
                })
        
        return data
    
    def get_export_headers(self, data_type):
        """
        获取导出表头
        """
        if data_type == '学生':
            return ['姓名', '联系方式', '标签']
        elif data_type == '教师':
            return ['姓名', '联系方式', '可教授课程类型']
        elif data_type == '课程':
            return ['课程名称', '教师姓名', '班级名称', '课程类型', '开始时间', '结束时间']
        elif data_type == '教材':
            return ['教材名称', '价格', '描述']
        return []
    
    def show_preview(self, data):
        """
        显示数据预览
        """
        if not data:
            self.preview_table.setRowCount(0)
            return
        
        headers = list(data[0].keys())
        self.preview_table.setColumnCount(len(headers))
        self.preview_table.setHorizontalHeaderLabels(headers)
        
        self.preview_table.setRowCount(min(len(data), 10))  # 最多显示10条
        
        for row, item in enumerate(data[:10]):
            for col, key in enumerate(headers):
                self.preview_table.setItem(row, col, QTableWidgetItem(str(item.get(key, ''))))