from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
                           QHeaderView, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt
from models import Textbook, Student
from database import db_manager

class TextbookStatsDialog(QDialog):
    """
    教材统计对话框
    """
    
    def __init__(self, parent=None):
        """
        初始化教材统计对话框
        """
        super().__init__(parent)
        self.init_ui()
        self.load_stats()
    
    def init_ui(self):
        """
        初始化UI界面
        """
        self.setWindowTitle('教材费用统计')
        self.resize(900, 700)
        
        layout = QVBoxLayout(self)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 按教材统计
        self.by_textbook_tab = self.create_by_textbook_tab()
        self.tab_widget.addTab(self.by_textbook_tab, '按教材统计')
        
        # 按学生统计
        self.by_student_tab = self.create_by_student_tab()
        self.tab_widget.addTab(self.by_student_tab, '按学生统计')
        
        layout.addWidget(self.tab_widget)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.load_stats)
        button_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton('导出')
        export_btn.clicked.connect(self.export_stats)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def create_by_textbook_tab(self):
        """
        创建按教材统计标签页
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 统计信息
        self.textbook_summary = QLabel('统计汇总: 0种教材, 0人使用, 总费用: 0元')
        self.textbook_summary.setStyleSheet('font-size: 14px; font-weight: bold; padding: 10px;')
        layout.addWidget(self.textbook_summary)
        
        # 统计表格
        self.textbook_table = QTableWidget()
        self.textbook_table.setColumnCount(7)
        self.textbook_table.setHorizontalHeaderLabels(['教材名称', '单价', '使用人数', '已发放', '未发放', '发放比例', '总费用'])
        self.textbook_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.textbook_table)
        
        return widget
    
    def create_by_student_tab(self):
        """
        创建按学生统计标签页
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 统计信息
        self.student_summary = QLabel('统计汇总: 0名学生, 总教材费用: 0元')
        self.student_summary.setStyleSheet('font-size: 14px; font-weight: bold; padding: 10px;')
        layout.addWidget(self.student_summary)
        
        # 统计表格
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(5)
        self.student_table.setHorizontalHeaderLabels(['学生姓名', '联系方式', '教材数量', '教材费用', '领取状态'])
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.student_table)
        
        return widget
    
    def load_stats(self):
        """
        加载统计数据
        """
        self.load_by_textbook_stats()
        self.load_by_student_stats()
    
    def load_by_textbook_stats(self):
        """
        加载按教材统计的数据
        """
        statistics = Textbook.get_statistics()
        
        total_textbooks = len(statistics)
        total_students = 0
        total_cost = 0.0
        
        self.textbook_table.setRowCount(len(statistics))
        
        for row, stat in enumerate(statistics):
            textbook_id, name, price, total_count, issued_count, cost = stat
            unissued_count = total_count - issued_count
            issue_ratio = f'{issued_count/total_count*100:.1f}%' if total_count > 0 else '0%'
            
            self.textbook_table.setItem(row, 0, QTableWidgetItem(name))
            self.textbook_table.setItem(row, 1, QTableWidgetItem(str(price)))
            self.textbook_table.setItem(row, 2, QTableWidgetItem(str(total_count)))
            self.textbook_table.setItem(row, 3, QTableWidgetItem(str(issued_count)))
            self.textbook_table.setItem(row, 4, QTableWidgetItem(str(unissued_count)))
            self.textbook_table.setItem(row, 5, QTableWidgetItem(issue_ratio))
            self.textbook_table.setItem(row, 6, QTableWidgetItem(str(cost)))
            
            total_students += total_count
            total_cost += cost
        
        self.textbook_summary.setText(
            f'统计汇总: {total_textbooks}种教材, {total_students}人使用, 总费用: {total_cost:.2f}元'
        )
    
    def load_by_student_stats(self):
        """
        加载按学生统计的数据
        """
        students = Student.get_all()
        
        total_students = len(students)
        total_cost = 0.0
        
        self.student_table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            # 获取学生的教材信息
            with db_manager as db:
                result = db.fetch_all('''
                    SELECT t.name, t.price, st.is_issued
                    FROM textbooks t
                    JOIN student_textbooks st ON t.id = st.textbook_id
                    WHERE st.student_id=?
                ''', (student.id,))
            
            textbook_count = len(result)
            student_cost = sum(t[1] for t in result)
            issued_count = sum(1 for t in result if t[2])
            
            if textbook_count > 0:
                status = f'{issued_count}/{textbook_count}'
            else:
                status = '无'
            
            self.student_table.setItem(row, 0, QTableWidgetItem(student.name))
            self.student_table.setItem(row, 1, QTableWidgetItem(student.contact))
            self.student_table.setItem(row, 2, QTableWidgetItem(str(textbook_count)))
            self.student_table.setItem(row, 3, QTableWidgetItem(f'{student_cost:.2f}'))
            self.student_table.setItem(row, 4, QTableWidgetItem(status))
            
            total_cost += student_cost
        
        self.student_summary.setText(
            f'统计汇总: {total_students}名学生, 总教材费用: {total_cost:.2f}元'
        )
    
    def export_stats(self):
        """
        导出统计数据
        """
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:
            # 导出按教材统计
            self.export_by_textbook()
        else:
            # 导出按学生统计
            self.export_by_student()
    
    def export_by_textbook(self):
        """
        导出按教材统计的数据
        """
        from PyQt5.QtWidgets import QFileDialog
        from utils.tools import write_csv_file
        
        data = []
        for row in range(self.textbook_table.rowCount()):
            data.append({
                '教材名称': self.textbook_table.item(row, 0).text(),
                '单价': self.textbook_table.item(row, 1).text(),
                '使用人数': self.textbook_table.item(row, 2).text(),
                '已发放': self.textbook_table.item(row, 3).text(),
                '未发放': self.textbook_table.item(row, 4).text(),
                '发放比例': self.textbook_table.item(row, 5).text(),
                '总费用': self.textbook_table.item(row, 6).text()
            })
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存教材统计数据', 
            '教材统计.csv', 
            'CSV文件 (*.csv);;所有文件 (*.*)'
        )
        
        if file_path:
            headers = ['教材名称', '单价', '使用人数', '已发放', '未发放', '发放比例', '总费用']
            if write_csv_file(file_path, data, headers):
                QMessageBox.information(self, '导出完成', '教材统计数据导出成功')
            else:
                QMessageBox.warning(self, '错误', '导出失败')
    
    def export_by_student(self):
        """
        导出按学生统计的数据
        """
        from PyQt5.QtWidgets import QFileDialog
        from utils.tools import write_csv_file
        
        data = []
        for row in range(self.student_table.rowCount()):
            data.append({
                '学生姓名': self.student_table.item(row, 0).text(),
                '联系方式': self.student_table.item(row, 1).text(),
                '教材数量': self.student_table.item(row, 2).text(),
                '教材费用': self.student_table.item(row, 3).text(),
                '领取状态': self.student_table.item(row, 4).text()
            })
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            '保存学生统计数据', 
            '学生统计.csv', 
            'CSV文件 (*.csv);;所有文件 (*.*)'
        )
        
        if file_path:
            headers = ['学生姓名', '联系方式', '教材数量', '教材费用', '领取状态']
            if write_csv_file(file_path, data, headers):
                QMessageBox.information(self, '导出完成', '学生统计数据导出成功')
            else:
                QMessageBox.warning(self, '错误', '导出失败')