from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QTextEdit, QPushButton, QLabel, QComboBox, 
                           QCalendarWidget, QMenuBar, QAction, QSplitter,
                           QTableWidget, QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont
import sys
from database import init_database, db_manager
from models import Student, Teacher, Course, Textbook

class MainWindow(QMainWindow):
    """
    主窗口类
    """
    
    def __init__(self):
        """
        初始化主窗口
        """
        super().__init__()
        self.init_ui()
        self.init_database()
    
    def init_ui(self):
        """
        初始化UI界面
        """
        # 设置窗口标题和大小
        self.setWindowTitle('课程表管理系统')
        self.resize(1200, 800)
        
        # 创建菜单
        self.create_menu()
        
        # 创建中央widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 创建左侧备忘录区域
        memo_widget = self.create_memo_widget()
        splitter.addWidget(memo_widget)
        
        # 创建中间课表区域
        schedule_widget = self.create_schedule_widget()
        splitter.addWidget(schedule_widget)
        
        # 创建右侧日历区域
        calendar_widget = self.create_calendar_widget()
        splitter.addWidget(calendar_widget)
        
        # 设置分割器大小
        splitter.setSizes([300, 600, 300])
    
    def create_menu(self):
        """
        创建菜单栏
        """
        menu_bar = self.menuBar()
        
        # 文件菜单
        file_menu = menu_bar.addMenu('文件')
        
        # 导入导出
        import_action = QAction('导入数据', self)
        export_action = QAction('导出数据', self)
        exit_action = QAction('退出', self)
        
        file_menu.addAction(import_action)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # 管理菜单
        manage_menu = menu_bar.addMenu('管理')
        
        # 人员管理
        student_action = QAction('学生管理', self)
        teacher_action = QAction('教师管理', self)
        
        # 课程管理
        course_action = QAction('课程管理', self)
        textbook_action = QAction('教材管理', self)
        
        manage_menu.addAction(student_action)
        manage_menu.addAction(teacher_action)
        manage_menu.addSeparator()
        manage_menu.addAction(course_action)
        manage_menu.addAction(textbook_action)
        
        # 统计菜单
        stats_menu = menu_bar.addMenu('统计')
        
        # 教材统计
        textbook_stats_action = QAction('教材费用统计', self)
        stats_menu.addAction(textbook_stats_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu('帮助')
        
        # 关于
        about_action = QAction('关于', self)
        help_menu.addAction(about_action)
    
    def create_memo_widget(self):
        """
        创建备忘录区域
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题
        title_label = QLabel('备忘录')
        title_label.setFont(QFont('SimHei', 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # 工具栏
        toolbar_layout = QHBoxLayout()
        
        # 字体大小按钮
        font_size_combo = QComboBox()
        font_size_combo.addItems(['小', '中', '大'])
        font_size_combo.setCurrentIndex(1)  # 默认中号
        toolbar_layout.addWidget(QLabel('字体大小:'))
        toolbar_layout.addWidget(font_size_combo)
        toolbar_layout.addStretch()
        
        layout.addLayout(toolbar_layout)
        
        # 编辑区
        self.memo_edit = QTextEdit()
        self.memo_edit.setPlainText('在此输入备忘录内容...')
        layout.addWidget(self.memo_edit)
        
        # 状态栏
        self.memo_status = QLabel('最后保存: 未保存')
        self.memo_status.setAlignment(Qt.AlignRight)
        layout.addWidget(self.memo_status)
        
        return widget
    
    def create_schedule_widget(self):
        """
        创建课表展示区域
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题栏
        title_layout = QHBoxLayout()
        
        # 周选择器
        self.week_combo = QComboBox()
        self.week_combo.addItems(['第1周', '第2周', '第3周', '第4周', '第5周'])
        title_layout.addWidget(QLabel('周:'))
        title_layout.addWidget(self.week_combo)
        
        # 视图切换
        self.view_combo = QComboBox()
        self.view_combo.addItems(['周视图', '日视图'])
        title_layout.addWidget(QLabel('视图:'))
        title_layout.addWidget(self.view_combo)
        
        title_layout.addStretch()
        
        # 操作按钮
        add_course_btn = QPushButton('添加课程')
        import_btn = QPushButton('导入')
        export_btn = QPushButton('导出')
        
        title_layout.addWidget(add_course_btn)
        title_layout.addWidget(import_btn)
        title_layout.addWidget(export_btn)
        
        layout.addLayout(title_layout)
        
        # 课表区域
        self.schedule_table = QTableWidget()
        self.schedule_table.setRowCount(12)  # 12个时间段
        self.schedule_table.setColumnCount(7)  # 7天
        
        # 设置表头
        headers = ['时间', '周一', '周二', '周三', '周四', '周五', '周六', '周日']
        self.schedule_table.setHorizontalHeaderLabels(headers)
        
        # 设置行高和列宽
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for i in range(12):
            self.schedule_table.setRowHeight(i, 60)
        
        # 填充时间行
        for i in range(12):
            hour = 8 + i
            time_str = f'{hour:02d}:00-{hour+1:02d}:00'
            self.schedule_table.setItem(i, 0, QTableWidgetItem(time_str))
            self.schedule_table.item(i, 0).setFlags(Qt.ItemIsEnabled)
        
        layout.addWidget(self.schedule_table)
        
        return widget
    
    def create_calendar_widget(self):
        """
        创建日历区域
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题
        title_label = QLabel('日历')
        title_label.setFont(QFont('SimHei', 14, QFont.Bold))
        layout.addWidget(title_label)
        
        # 日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        layout.addWidget(self.calendar)
        
        # 日期导航
        nav_layout = QHBoxLayout()
        prev_btn = QPushButton('上月')
        next_btn = QPushButton('下月')
        nav_layout.addWidget(prev_btn)
        nav_layout.addWidget(next_btn)
        layout.addLayout(nav_layout)
        
        # 选中日期信息
        self.date_info = QLabel(f'选中日期: {QDate.currentDate().toString()}')
        self.date_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.date_info)
        
        return widget
    
    def init_database(self):
        """
        初始化数据库
        """
        init_database()
        print('数据库初始化完成')
    
    def closeEvent(self, event):
        """
        关闭窗口事件
        """
        # 保存备忘录
        self.save_memo()
        event.accept()
    
    def save_memo(self):
        """
        保存备忘录内容
        """
        content = self.memo_edit.toPlainText()
        with db_manager as db:
            # 检查是否存在备忘录记录
            result = db.fetch_one('SELECT id FROM memos WHERE id=1')
            if result:
                # 更新
                db.execute('UPDATE memos SET content=?, updated_at=CURRENT_TIMESTAMP WHERE id=1', (content,))
            else:
                # 插入
                db.execute('INSERT INTO memos (id, content) VALUES (?, ?)', (1, content))
        
        # 更新状态
        self.memo_status.setText(f'最后保存: {QDate.currentDate().toString()} {QTime.currentTime().toString()}')

def main():
    """
    主函数
    """
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()