from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                           QHeaderView, QMessageBox)
from PyQt5.QtCore import Qt
from models import Textbook

class TextbookManagerDialog(QDialog):
    """
    教材管理对话框
    """
    
    def __init__(self, parent=None):
        """
        初始化教材管理对话框
        """
        super().__init__(parent)
        self.current_textbook = None
        self.init_ui()
        self.load_textbooks()
    
    def init_ui(self):
        """
        初始化UI界面
        """
        self.setWindowTitle('教材管理')
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # 搜索区域
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel('搜索:'))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入教材名称搜索...')
        search_layout.addWidget(self.search_input)
        
        search_btn = QPushButton('搜索')
        search_btn.clicked.connect(self.search_textbooks)
        search_layout.addWidget(search_btn)
        
        refresh_btn = QPushButton('刷新')
        refresh_btn.clicked.connect(self.load_textbooks)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # 教材列表
        self.textbook_table = QTableWidget()
        self.textbook_table.setColumnCount(3)
        self.textbook_table.setHorizontalHeaderLabels(['教材名称', '价格', '描述'])
        self.textbook_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.textbook_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.textbook_table.setSelectionMode(QTableWidget.SingleSelection)
        self.textbook_table.doubleClicked.connect(self.edit_textbook)
        layout.addWidget(self.textbook_table)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton('添加教材')
        add_btn.clicked.connect(self.add_textbook)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton('编辑教材')
        edit_btn.clicked.connect(self.edit_textbook)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton('删除教材')
        delete_btn.clicked.connect(self.delete_textbook)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton('关闭')
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def load_textbooks(self):
        """
        加载所有教材
        """
        textbooks = Textbook.get_all()
        self.update_table(textbooks)
    
    def search_textbooks(self):
        """
        搜索教材
        """
        keyword = self.search_input.text().strip()
        if not keyword:
            self.load_textbooks()
            return
        
        textbooks = Textbook.search_by_name(keyword)
        self.update_table(textbooks)
    
    def update_table(self, textbooks):
        """
        更新表格显示
        """
        self.textbook_table.setRowCount(len(textbooks))
        for row, textbook in enumerate(textbooks):
            self.textbook_table.setItem(row, 0, QTableWidgetItem(textbook.name))
            self.textbook_table.setItem(row, 1, QTableWidgetItem(str(textbook.price)))
            self.textbook_table.setItem(row, 2, QTableWidgetItem(textbook.description))
    
    def add_textbook(self):
        """
        添加教材
        """
        dialog = TextbookEditDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_textbooks()
    
    def edit_textbook(self):
        """
        编辑教材
        """
        selected = self.textbook_table.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一个教材')
            return
        
        row = selected[0].row()
        textbook_name = self.textbook_table.item(row, 0).text()
        textbooks = Textbook.search_by_name(textbook_name)
        
        if textbooks:
            dialog = TextbookEditDialog(self, textbooks[0])
            if dialog.exec_() == QDialog.Accepted:
                self.load_textbooks()
    
    def delete_textbook(self):
        """
        删除教材
        """
        selected = self.textbook_table.selectedIndexes()
        if not selected:
            QMessageBox.warning(self, '提示', '请先选择一个教材')
            return
        
        row = selected[0].row()
        textbook_name = self.textbook_table.item(row, 0).text()
        
        reply = QMessageBox.question(self, '确认删除', 
                                    f'确定要删除教材 "{textbook_name}" 吗？',
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            textbooks = Textbook.search_by_name(textbook_name)
            if textbooks:
                textbooks[0].delete()
                self.load_textbooks()

class TextbookEditDialog(QDialog):
    """
    教材编辑对话框
    """
    
    def __init__(self, parent=None, textbook=None):
        """
        初始化教材编辑对话框
        """
        super().__init__(parent)
        self.textbook = textbook
        self.init_ui()
    
    def init_ui(self):
        """
        初始化UI界面
        """
        self.setWindowTitle('编辑教材' if self.textbook else '添加教材')
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        
        # 教材名称
        layout.addWidget(QLabel('教材名称:'))
        self.name_input = QLineEdit()
        if self.textbook:
            self.name_input.setText(self.textbook.name)
        layout.addWidget(self.name_input)
        
        # 价格
        layout.addWidget(QLabel('价格:'))
        self.price_input = QLineEdit()
        if self.textbook:
            self.price_input.setText(str(self.textbook.price))
        layout.addWidget(self.price_input)
        
        # 描述
        layout.addWidget(QLabel('描述:'))
        self.description_input = QLineEdit()
        if self.textbook:
            self.description_input.setText(self.textbook.description)
        layout.addWidget(self.description_input)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self.save_textbook)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def save_textbook(self):
        """
        保存教材信息
        """
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, '提示', '教材名称不能为空')
            return
        
        price_text = self.price_input.text().strip()
        try:
            price = float(price_text) if price_text else 0.0
        except ValueError:
            QMessageBox.warning(self, '提示', '价格必须是数字')
            return
        
        if self.textbook:
            # 更新现有教材
            self.textbook.name = name
            self.textbook.price = price
            self.textbook.description = self.description_input.text().strip()
            self.textbook.save()
        else:
            # 创建新教材
            textbook = Textbook(
                name=name,
                price=price,
                description=self.description_input.text().strip()
            )
            textbook.save()
        
        self.accept()