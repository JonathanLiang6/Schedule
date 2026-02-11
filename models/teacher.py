from database import db_manager

class Teacher:
    """
    教师模型类
    """
    
    def __init__(self, id=None, name='', contact='', subject_types=''):
        """
        初始化教师对象
        """
        self.id = id
        self.name = name
        self.contact = contact
        self.subject_types = subject_types
    
    def save(self):
        """
        保存教师信息到数据库
        """
        with db_manager as db:
            if self.id is None:
                # 新增教师
                db.execute(
                    'INSERT INTO teachers (name, contact, subject_types) VALUES (?, ?, ?)',
                    (self.name, self.contact, self.subject_types)
                )
                self.id = db.get_last_insert_id()
            else:
                # 更新教师信息
                db.execute(
                    'UPDATE teachers SET name=?, contact=?, subject_types=? WHERE id=?',
                    (self.name, self.contact, self.subject_types, self.id)
                )
        return self.id
    
    def delete(self):
        """
        从数据库中删除教师
        """
        if self.id:
            with db_manager as db:
                # 先删除关联数据
                db.execute('DELETE FROM courses WHERE teacher_id=?', (self.id,))
                db.execute('DELETE FROM available_times WHERE person_id=? AND person_type=?', (self.id, 'teacher'))
                # 删除教师
                db.execute('DELETE FROM teachers WHERE id=?', (self.id,))
    
    def set_available_time(self, day_of_week, start_time, end_time):
        """
        设置教师的可用时间
        """
        if self.id:
            with db_manager as db:
                db.execute(
                    'INSERT OR REPLACE INTO available_times (person_id, person_type, day_of_week, start_time, end_time) VALUES (?, ?, ?, ?, ?)',
                    (self.id, 'teacher', day_of_week, start_time, end_time)
                )
    
    def get_available_times(self):
        """
        获取教师的可用时间
        """
        if self.id:
            with db_manager as db:
                result = db.fetch_all(
                    'SELECT day_of_week, start_time, end_time FROM available_times WHERE person_id=? AND person_type=?',
                    (self.id, 'teacher')
                )
                return result
        return []
    
    def can_teach(self, subject_type):
        """
        检查教师是否可以教授某课程类型
        """
        if not self.subject_types:
            return False
        return subject_type in self.subject_types.split(',')
    
    @classmethod
    def get_by_id(cls, teacher_id):
        """
        根据ID获取教师对象
        """
        with db_manager as db:
            result = db.fetch_one('SELECT id, name, contact, subject_types FROM teachers WHERE id=?', (teacher_id,))
            if result:
                return cls(id=result[0], name=result[1], contact=result[2], subject_types=result[3])
            return None
    
    @classmethod
    def get_all(cls):
        """
        获取所有教师
        """
        with db_manager as db:
            results = db.fetch_all('SELECT id, name, contact, subject_types FROM teachers ORDER BY name')
            return [cls(id=row[0], name=row[1], contact=row[2], subject_types=row[3]) for row in results]
    
    @classmethod
    def search_by_name(cls, name):
        """
        根据姓名搜索教师
        """
        with db_manager as db:
            results = db.fetch_all(
                'SELECT id, name, contact, subject_types FROM teachers WHERE name LIKE ? ORDER BY name',
                (f'%{name}%',)
            )
            return [cls(id=row[0], name=row[1], contact=row[2], subject_types=row[3]) for row in results]
    
    @classmethod
    def get_teachers_by_subject(cls, subject_type):
        """
        根据课程类型获取教师
        """
        with db_manager as db:
            results = db.fetch_all(
                'SELECT id, name, contact, subject_types FROM teachers WHERE subject_types LIKE ? ORDER BY name',
                (f'%{subject_type}%',)
            )
            return [cls(id=row[0], name=row[1], contact=row[2], subject_types=row[3]) for row in results]

# 测试函数
def test_teacher_model():
    """
    测试教师模型
    """
    # 创建测试教师
    teacher = Teacher(name='张老师', contact='13900139000', subject_types='数学,物理')
    teacher_id = teacher.save()
    print(f"创建教师成功，ID: {teacher_id}")
    
    # 设置可用时间
    teacher.set_available_time(1, '09:00', '12:00')  # 周一上午
    available_times = teacher.get_available_times()
    print(f"教师可用时间: {available_times}")
    
    # 检查是否可以教授某课程
    print(f"是否可以教授数学: {teacher.can_teach('数学')}")
    print(f"是否可以教授英语: {teacher.can_teach('英语')}")
    
    # 搜索教师
    teachers = Teacher.search_by_name('张')
    print(f"搜索结果: {[t.name for t in teachers]}")
    
    # 按课程类型获取教师
    math_teachers = Teacher.get_teachers_by_subject('数学')
    print(f"数学教师: {[t.name for t in math_teachers]}")
    
    # 清理测试数据
    teacher.delete()
    print("测试完成")

if __name__ == "__main__":
    test_teacher_model()