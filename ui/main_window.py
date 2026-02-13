from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QTextEdit, QPushButton, QLabel, QComboBox, 
                           QCalendarWidget, QMenuBar, QAction, QSplitter,
                           QTableWidget, QTableWidgetItem, QHeaderView,
                           QMessageBox, QDialog, QListWidget, QListWidgetItem,
                           QLineEdit, QInputDialog)
from PyQt5.QtCore import Qt, QDate, QTime
from PyQt5.QtGui import QFont, QTextCharFormat
import sys
from database import init_database, db_manager
from models import Student, Teacher, Course, Textbook
from .student_dialog import StudentManagerDialog
from .teacher_dialog import TeacherManagerDialog
from .course_dialog import CourseManagerDialog
from .textbook_dialog import TextbookManagerDialog
from .import_export_dialog import ImportExportDialog
from .textbook_stats_dialog import TextbookStatsDialog

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
        import_action.triggered.connect(self.import_data)
        export_action = QAction('导出数据', self)
        export_action.triggered.connect(self.export_data)
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        
        file_menu.addAction(import_action)
        file_menu.addAction(export_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)
        
        # 管理菜单
        manage_menu = menu_bar.addMenu('管理')
        
        # 人员管理
        student_action = QAction('学生管理', self)
        student_action.triggered.connect(self.open_student_manager)
        teacher_action = QAction('教师管理', self)
        teacher_action.triggered.connect(self.open_teacher_manager)
        
        # 课程管理
        course_action = QAction('课程管理', self)
        course_action.triggered.connect(self.open_course_manager)
        textbook_action = QAction('教材管理', self)
        textbook_action.triggered.connect(self.open_textbook_manager)
        
        manage_menu.addAction(student_action)
        manage_menu.addAction(teacher_action)
        manage_menu.addSeparator()
        manage_menu.addAction(course_action)
        manage_menu.addAction(textbook_action)
        
        # 统计菜单
        stats_menu = menu_bar.addMenu('统计')
        
        # 教材统计
        textbook_stats_action = QAction('教材费用统计', self)
        textbook_stats_action.triggered.connect(self.open_textbook_stats)
        stats_menu.addAction(textbook_stats_action)
        
        # 帮助菜单
        help_menu = menu_bar.addMenu('帮助')
        
        # 关于
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
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
        font_size_combo.currentIndexChanged.connect(self.change_memo_font_size)
        self.font_size_combo = font_size_combo
        toolbar_layout.addWidget(QLabel('字体大小:'))
        toolbar_layout.addWidget(font_size_combo)
        
        toolbar_layout.addStretch()
        
        # 添加按钮
        add_memo_btn = QPushButton('添加')
        add_memo_btn.clicked.connect(self.add_memo)
        toolbar_layout.addWidget(add_memo_btn)
        
        # 删除按钮
        delete_memo_btn = QPushButton('删除')
        delete_memo_btn.clicked.connect(self.delete_memo)
        toolbar_layout.addWidget(delete_memo_btn)
        
        layout.addLayout(toolbar_layout)
        
        # 备忘录列表
        self.memo_list = QListWidget()
        self.memo_list.itemDoubleClicked.connect(self.edit_memo_item)
        layout.addWidget(self.memo_list)
        
        # 状态栏
        self.memo_status = QLabel('最后保存: 未保存')
        self.memo_status.setAlignment(Qt.AlignRight)
        layout.addWidget(self.memo_status)
        
        # 加载当前日期的备忘录
        self.current_date = QDate.currentDate().toString('yyyy-MM-dd')
        self.load_memo_by_date(self.current_date)
        
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
        self.week_combo.currentIndexChanged.connect(self.refresh_schedule)
        title_layout.addWidget(QLabel('周:'))
        title_layout.addWidget(self.week_combo)
        
        # 视图切换
        self.view_combo = QComboBox()
        self.view_combo.addItems(['周视图', '日视图'])
        self.view_combo.currentIndexChanged.connect(self.refresh_schedule)
        title_layout.addWidget(QLabel('视图:'))
        title_layout.addWidget(self.view_combo)
        
        title_layout.addStretch()
        
        # 操作按钮
        add_course_btn = QPushButton('添加课程')
        add_course_btn.clicked.connect(self.open_course_manager)
        import_btn = QPushButton('导入')
        import_btn.clicked.connect(self.import_data)
        export_btn = QPushButton('导出')
        export_btn.clicked.connect(self.export_data)
        
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
        
        # 双击事件
        self.schedule_table.cellDoubleClicked.connect(self.on_schedule_double_click)
        
        layout.addWidget(self.schedule_table)
        
        # 刷新课表
        self.refresh_schedule()
        
        return widget
    
    def create_calendar_widget(self):
        """
        创建日历区域
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 标题栏
        title_layout = QHBoxLayout()
        
        # 日期导航按钮（纯线条符号）
        prev_btn = QPushButton('◀')
        prev_btn.setFixedSize(30, 30)
        prev_btn.clicked.connect(self.calendar.showPreviousMonth)
        
        next_btn = QPushButton('▶')
        next_btn.setFixedSize(30, 30)
        next_btn.clicked.connect(self.calendar.showNextMonth)
        
        title_layout.addWidget(prev_btn)
        title_layout.addStretch()
        title_layout.addWidget(next_btn)
        
        layout.addLayout(title_layout)
        
        # 日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_calendar_clicked)
        layout.addWidget(self.calendar)
        
        # 选中日期信息
        self.date_info = QLabel(f'选中日期: {QDate.currentDate().toString()}')
        self.date_info.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.date_info)
        
        # 标记有课程的日期
        self.mark_calendar_dates()
        
        return widget
    
    def on_calendar_clicked(self, date):
        """
        日历点击事件
        """
        date_str = date.toString('yyyy-MM-dd')
        self.date_info.setText(f'选中日期: {date_str}')
        
        # 更新当前日期并加载该日期的备忘录
        self.current_date = date_str
        self.load_memo_by_date(date_str)
        
        # 查找该日期的课程
        courses = Course.get_all()
        courses_on_date = []
        
        for course in courses:
            try:
                course_date = course.start_time.split()[0]
                if course_date == date_str:
                    courses_on_date.append(course)
            except:
                pass
        
        if courses_on_date:
            # 显示该日期的课程
            course_list = '\n'.join([f'{c.name} ({c.start_time.split()[1][:5]}-{c.end_time.split()[1][:5]})' for c in courses_on_date])
            reply = QMessageBox.question(
                self, 
                f'{date_str} 的课程', 
                f'{date_str} 有 {len(courses_on_date)} 门课程:\n\n{course_list}\n\n是否打开当日课表？',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 打开当日课表
                self.open_course_manager()
        else:
            QMessageBox.information(self, '提示', f'{date_str} 没有课程安排')
    
    def mark_calendar_dates(self):
        """
        标记有课程的日期
        """
        # 获取所有课程
        courses = Course.get_all()
        
        # 使用 QTextCharFormat 来标记日期
        from PyQt5.QtGui import QColor, QBrush
        
        # 创建标记格式
        format = QTextCharFormat()
        format.setBackground(QBrush(QColor(100, 149, 237)))  # 矢车菊蓝
        format.setForeground(QBrush(QColor(255, 255, 255)))
        
        # 标记有课程的日期
        for course in courses:
            try:
                date = QDate.fromString(course.start_time.split()[0], 'yyyy-MM-dd')
                self.calendar.setDateTextFormat(date, format)
            except:
                pass
    
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
        event.accept()
    
    def load_memo_by_date(self, date):
        """
        加载指定日期的备忘录
        """
        self.memo_list.clear()
        with db_manager as db:
            result = db.fetch_all('SELECT id, content, font_size FROM memos WHERE date=? ORDER BY created_at', (date,))
            for row in result:
                memo_id, content, font_size = row
                item = QListWidgetItem(content)
                item.setData(Qt.UserRole, memo_id)
                item.setData(Qt.UserRole + 1, font_size)
                self.memo_list.addItem(item)
                self.apply_font_size_to_item(item, font_size)
    
    def add_memo(self):
        """
        添加备忘录
        """
        content, ok = QInputDialog.getText(self, '添加备忘录', '请输入备忘录内容:')
        if ok and content.strip():
            with db_manager as db:
                font_sizes = [10, 12, 14]
                font_size = font_sizes[self.font_size_combo.currentIndex()]
                db.execute('INSERT INTO memos (content, date, font_size) VALUES (?, ?, ?)', 
                          (content.strip(), self.current_date, font_size))
            
            self.load_memo_by_date(self.current_date)
            self.memo_status.setText(f'最后保存: {QDate.currentDate().toString()} {QTime.currentTime().toString()}')
    
    def edit_memo_item(self, item):
        """
        编辑备忘录项
        """
        old_content = item.text()
        new_content, ok = QInputDialog.getText(self, '编辑备忘录', '请修改备忘录内容:', text=old_content)
        if ok and new_content.strip() and new_content != old_content:
            memo_id = item.data(Qt.UserRole)
            with db_manager as db:
                db.execute('UPDATE memos SET content=?, updated_at=CURRENT_TIMESTAMP WHERE id=?', 
                          (new_content.strip(), memo_id))
            
            self.load_memo_by_date(self.current_date)
            self.memo_status.setText(f'最后保存: {QDate.currentDate().toString()} {QTime.currentTime().toString()}')
    
    def delete_memo(self):
        """
        删除选中的备忘录
        """
        selected_items = self.memo_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '提示', '请先选择要删除的备忘录')
            return
        
        reply = QMessageBox.question(self, '确认删除', 
                                    f'确定要删除选中的 {len(selected_items)} 条备忘录吗？',
                                    QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            with db_manager as db:
                for item in selected_items:
                    memo_id = item.data(Qt.UserRole)
                    db.execute('DELETE FROM memos WHERE id=?', (memo_id,))
            
            self.load_memo_by_date(self.current_date)
            self.memo_status.setText(f'最后保存: {QDate.currentDate().toString()} {QTime.currentTime().toString()}')
    
    def change_memo_font_size(self, index):
        """
        改变选中备忘录的字体大小
        """
        font_sizes = [10, 12, 14]
        font_size = font_sizes[index]
        
        # 获取选中的备忘录项
        selected_items = self.memo_list.selectedItems()
        
        if selected_items:
            # 只应用到选中的备忘录项
            for item in selected_items:
                self.apply_font_size_to_item(item, font_size)
                
                # 更新数据库中的字体大小
                memo_id = item.data(Qt.UserRole)
                with db_manager as db:
                    db.execute('UPDATE memos SET font_size=? WHERE id=?', (font_size, memo_id))
            
            self.memo_status.setText(f'最后保存: {QDate.currentDate().toString()} {QTime.currentTime().toString()}')
    
    def apply_font_size_to_item(self, item, font_size):
        """
        应用字体大小到备忘录项
        """
        font = QFont()
        font.setPointSize(font_size)
        item.setFont(font)
    
    def refresh_schedule(self):
        """
        刷新课表显示
        """
        # 清空课表
        for row in range(self.schedule_table.rowCount()):
            for col in range(1, self.schedule_table.columnCount()):
                item = self.schedule_table.item(row, col)
                if item:
                    self.schedule_table.setItem(row, col, QTableWidgetItem())
        
        # 获取所有课程
        courses = Course.get_all()
        
        # 显示课程
        for course in courses:
            try:
                start_dt = QDate.fromString(course.start_time.split()[0], 'yyyy-MM-dd')
                start_time = course.start_time.split()[1][:5]
                end_time = course.end_time.split()[1][:5]
                
                # 计算星期几
                day_of_week = start_dt.dayOfWeek() - 1  # Qt的dayOfWeek()返回1-7，我们需要0-6
                
                # 计算时间段
                hour = int(start_time.split(':')[0])
                row = hour - 8  # 从8点开始
                
                if 0 <= row < 12 and 0 <= day_of_week < 7:
                    # 显示课程信息
                    item = QTableWidgetItem(f'{course.name}\n{course.get_teacher_name()}\n{start_time}-{end_time}')
                    self.schedule_table.setItem(row, day_of_week + 1, item)
            except:
                pass
    
    def on_schedule_double_click(self, row, col):
        """
        课表双击事件
        """
        if col == 0:
            return
        
        item = self.schedule_table.item(row, col)
        if item and item.text():
            # 双击了课程，打开编辑对话框
            QMessageBox.information(self, '提示', '双击课程编辑功能待实现')
        else:
            # 双击了空白区域，打开添加课程对话框
            self.open_course_manager()
    
    def open_student_manager(self):
        """
        打开学生管理对话框
        """
        dialog = StudentManagerDialog(self)
        dialog.exec_()
    
    def open_teacher_manager(self):
        """
        打开教师管理对话框
        """
        dialog = TeacherManagerDialog(self)
        dialog.exec_()
    
    def open_course_manager(self):
        """
        打开课程管理对话框
        """
        dialog = CourseManagerDialog(self)
        dialog.exec_()
        self.refresh_schedule()
    
    def open_textbook_manager(self):
        """
        打开教材管理对话框
        """
        dialog = TextbookManagerDialog(self)
        dialog.exec_()
    
    def open_textbook_stats(self):
        """
        打开教材统计对话框
        """
        dialog = TextbookStatsDialog(self)
        dialog.exec_()
    
    def import_data(self):
        """
        导入数据
        """
        dialog = ImportExportDialog(self)
        dialog.exec_()
    
    def export_data(self):
        """
        导出数据
        """
        dialog = ImportExportDialog(self)
        dialog.exec_()
    
    def show_about(self):
        """
        显示关于对话框
        """
        QMessageBox.about(self, '关于', 
                        '课程表管理系统 v1.0\n\n'
                        '一款基于Python开发的Windows桌面应用程序，\n'
                        '专门用于教育机构的课程安排与管理工作。')

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