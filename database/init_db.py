import sqlite3
import os

def init_database(db_path='schedule.db'):
    """
    初始化数据库，创建所需的数据表
    """
    # 检查数据库文件是否存在
    db_exists = os.path.exists(db_path)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建学生表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT,
        tags TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建教师表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS teachers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        contact TEXT,
        subject_types TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建课程表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        teacher_id INTEGER,
        class_name TEXT,
        course_type TEXT,
        start_time TEXT,
        end_time TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (teacher_id) REFERENCES teachers (id)
    )''')
    
    # 创建教材表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS textbooks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建时间可用表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS available_times (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        person_id INTEGER,
        person_type TEXT,
        day_of_week INTEGER,
        start_time TEXT,
        end_time TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建备忘录表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS memos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        date TEXT NOT NULL,
        font_size INTEGER DEFAULT 12,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # 创建学生-班级关联表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS student_classes (
        student_id INTEGER,
        class_name TEXT,
        PRIMARY KEY (student_id, class_name),
        FOREIGN KEY (student_id) REFERENCES students (id)
    )''')
    
    # 创建课程-学生关联表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS course_students (
        course_id INTEGER,
        student_id INTEGER,
        PRIMARY KEY (course_id, student_id),
        FOREIGN KEY (course_id) REFERENCES courses (id),
        FOREIGN KEY (student_id) REFERENCES students (id)
    )''')
    
    # 创建学生-教材关联表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS student_textbooks (
        student_id INTEGER,
        textbook_id INTEGER,
        is_issued INTEGER DEFAULT 0,
        is_paid INTEGER DEFAULT 0,
        PRIMARY KEY (student_id, textbook_id),
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (textbook_id) REFERENCES textbooks (id)
    )''')
    
    # 提交事务
    conn.commit()
    
    # 关闭连接
    conn.close()
    
    if not db_exists:
        print(f"数据库 {db_path} 已创建并初始化成功！")
    else:
        print(f"数据库 {db_path} 已存在，表结构已更新！")

if __name__ == "__main__":
    init_database()