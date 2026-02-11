from database import db_manager

class Student:
    """
    学生模型类
    """
    
    def __init__(self, id=None, name='', contact='', tags=''):
        """
        初始化学生对象
        """
        self.id = id
        self.name = name
        self.contact = contact
        self.tags = tags
    
    def save(self):
        """
        保存学生信息到数据库
        """
        with db_manager as db:
            if self.id is None:
                # 新增学生
                db.execute(
                    'INSERT INTO students (name, contact, tags) VALUES (?, ?, ?)',
                    (self.name, self.contact, self.tags)
                )
                self.id = db.get_last_insert_id()
            else:
                # 更新学生信息
                db.execute(
                    'UPDATE students SET name=?, contact=?, tags=? WHERE id=?',
                    (self.name, self.contact, self.tags, self.id)
                )
        return self.id
    
    def delete(self):
        """
        从数据库中删除学生
        """
        if self.id:
            with db_manager as db:
                # 先删除关联数据
                db.execute('DELETE FROM student_classes WHERE student_id=?', (self.id,))
                db.execute('DELETE FROM course_students WHERE student_id=?', (self.id,))
                db.execute('DELETE FROM student_textbooks WHERE student_id=?', (self.id,))
                db.execute('DELETE FROM available_times WHERE person_id=? AND person_type=?', (self.id, 'student'))
                # 删除学生
                db.execute('DELETE FROM students WHERE id=?', (self.id,))
    
    def add_class(self, class_name):
        """
        为学生添加班级
        """
        if self.id:
            with db_manager as db:
                db.execute(
                    'INSERT OR IGNORE INTO student_classes (student_id, class_name) VALUES (?, ?)',
                    (self.id, class_name)
                )
    
    def remove_class(self, class_name):
        """
        从学生中移除班级
        """
        if self.id:
            with db_manager as db:
                db.execute(
                    'DELETE FROM student_classes WHERE student_id=? AND class_name=?',
                    (self.id, class_name)
                )
    
    def get_classes(self):
        """
        获取学生所属的班级
        """
        if self.id:
            with db_manager as db:
                result = db.fetch_all(
                    'SELECT class_name FROM student_classes WHERE student_id=?',
                    (self.id,)
                )
                return [row[0] for row in result]
        return []
    
    def add_textbook(self, textbook_id, is_issued=0):
        """
        为学生添加教材
        """
        if self.id:
            with db_manager as db:
                db.execute(
                    'INSERT OR REPLACE INTO student_textbooks (student_id, textbook_id, is_issued) VALUES (?, ?, ?)',
                    (self.id, textbook_id, is_issued)
                )
    
    def set_available_time(self, day_of_week, start_time, end_time):
        """
        设置学生的可用时间
        """
        if self.id:
            with db_manager as db:
                db.execute(
                    'INSERT OR REPLACE INTO available_times (person_id, person_type, day_of_week, start_time, end_time) VALUES (?, ?, ?, ?, ?)',
                    (self.id, 'student', day_of_week, start_time, end_time)
                )
    
    @classmethod
    def get_by_id(cls, student_id):
        """
        根据ID获取学生对象
        """
        with db_manager as db:
            result = db.fetch_one('SELECT id, name, contact, tags FROM students WHERE id=?', (student_id,))
            if result:
                return cls(id=result[0], name=result[1], contact=result[2], tags=result[3])
            return None
    
    @classmethod
    def get_all(cls):
        """
        获取所有学生
        """
        with db_manager as db:
            results = db.fetch_all('SELECT id, name, contact, tags FROM students ORDER BY name')
            return [cls(id=row[0], name=row[1], contact=row[2], tags=row[3]) for row in results]
    
    @classmethod
    def search_by_name(cls, name):
        """
        根据姓名搜索学生
        """
        with db_manager as db:
            results = db.fetch_all(
                'SELECT id, name, contact, tags FROM students WHERE name LIKE ? ORDER BY name',
                (f'%{name}%',)
            )
            return [cls(id=row[0], name=row[1], contact=row[2], tags=row[3]) for row in results]
    
    @classmethod
    def search_by_tag(cls, tag):
        """
        根据标签搜索学生
        """
        with db_manager as db:
            results = db.fetch_all(
                'SELECT id, name, contact, tags FROM students WHERE tags LIKE ? ORDER BY name',
                (f'%{tag}%',)
            )
            return [cls(id=row[0], name=row[1], contact=row[2], tags=row[3]) for row in results]

# 测试函数
def test_student_model():
    """
    测试学生模型
    """
    # 创建测试学生
    student = Student(name='张三', contact='13800138000', tags='数学班,英语班')
    student_id = student.save()
    print(f"创建学生成功，ID: {student_id}")
    
    # 添加班级
    student.add_class('高一数学班')
    student.add_class('高一英语班')
    classes = student.get_classes()
    print(f"学生班级: {classes}")
    
    # 搜索学生
    students = Student.search_by_name('张')
    print(f"搜索结果: {[s.name for s in students]}")
    
    # 清理测试数据
    student.delete()
    print("测试完成")

if __name__ == "__main__":
    test_student_model()