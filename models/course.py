from database import db_manager
from datetime import datetime

class Course:
    """
    课程模型类
    """
    
    def __init__(self, id=None, name='', teacher_id=None, class_name='', course_type='', start_time='', end_time=''):
        """
        初始化课程对象
        """
        self.id = id
        self.name = name
        self.teacher_id = teacher_id
        self.class_name = class_name
        self.course_type = course_type
        self.start_time = start_time
        self.end_time = end_time
    
    def save(self):
        """
        保存课程信息到数据库
        """
        # 检查时间冲突
        if self.id is None:
            if self.check_conflicts():
                raise Exception('时间冲突：该时间段已有其他安排')
        
        with db_manager as db:
            if self.id is None:
                # 新增课程
                db.execute(
                    'INSERT INTO courses (name, teacher_id, class_name, course_type, start_time, end_time) VALUES (?, ?, ?, ?, ?, ?)',
                    (self.name, self.teacher_id, self.class_name, self.course_type, self.start_time, self.end_time)
                )
                self.id = db.get_last_insert_id()
            else:
                # 检查更新后的时间冲突
                if self.check_conflicts():
                    raise Exception('时间冲突：该时间段已有其他安排')
                # 更新课程信息
                db.execute(
                    'UPDATE courses SET name=?, teacher_id=?, class_name=?, course_type=?, start_time=?, end_time=? WHERE id=?',
                    (self.name, self.teacher_id, self.class_name, self.course_type, self.start_time, self.end_time, self.id)
                )
        return self.id
    
    def delete(self):
        """
        从数据库中删除课程
        """
        if self.id:
            with db_manager as db:
                # 先删除关联数据
                db.execute('DELETE FROM course_students WHERE course_id=?', (self.id,))
                # 删除课程
                db.execute('DELETE FROM courses WHERE id=?', (self.id,))
    
    def add_student(self, student_id):
        """
        为课程添加学生
        """
        if self.id:
            with db_manager as db:
                db.execute(
                    'INSERT OR IGNORE INTO course_students (course_id, student_id) VALUES (?, ?)',
                    (self.id, student_id)
                )
    
    def remove_student(self, student_id):
        """
        从课程中移除学生
        """
        if self.id:
            with db_manager as db:
                db.execute(
                    'DELETE FROM course_students WHERE course_id=? AND student_id=?',
                    (self.id, student_id)
                )
    
    def get_students(self):
        """
        获取课程的学生
        """
        if self.id:
            with db_manager as db:
                result = db.fetch_all(
                    'SELECT student_id FROM course_students WHERE course_id=?',
                    (self.id,)
                )
                return [row[0] for row in result]
        return []
    
    def check_conflicts(self):
        """
        检查课程时间冲突
        """
        if not self.start_time or not self.end_time:
            return False
        
        # 检查教师时间冲突
        if self.teacher_id:
            with db_manager as db:
                # 获取教师在同一时间段的其他课程
                query = '''
                SELECT COUNT(*) FROM courses 
                WHERE teacher_id=? AND start_time < ? AND end_time > ?
                '''
                if self.id:
                    query += ' AND id != ?'
                    params = (self.teacher_id, self.end_time, self.start_time, self.id)
                else:
                    params = (self.teacher_id, self.end_time, self.start_time)
                
                result = db.fetch_one(query, params)
                if result[0] > 0:
                    return True
        
        # 检查学生时间冲突（如果已添加学生）
        if self.id:
            students = self.get_students()
            for student_id in students:
                with db_manager as db:
                    # 获取学生在同一时间段的其他课程
                    query = '''
                    SELECT COUNT(*) FROM courses c
                    JOIN course_students cs ON c.id = cs.course_id
                    WHERE cs.student_id=? AND c.start_time < ? AND c.end_time > ? AND c.id != ?
                    '''
                    result = db.fetch_one(query, (student_id, self.end_time, self.start_time, self.id))
                    if result[0] > 0:
                        return True
        
        return False
    
    def get_teacher_name(self):
        """
        获取教师姓名
        """
        if self.teacher_id:
            with db_manager as db:
                result = db.fetch_one('SELECT name FROM teachers WHERE id=?', (self.teacher_id,))
                if result:
                    return result[0]
        return ''
    
    def get_duration(self):
        """
        计算课程持续时间（分钟）
        """
        if not self.start_time or not self.end_time:
            return 0
        
        try:
            start = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M')
            end = datetime.strptime(self.end_time, '%Y-%m-%d %H:%M')
            duration = (end - start).total_seconds() / 60
            return int(duration)
        except:
            return 0
    
    @classmethod
    def get_by_id(cls, course_id):
        """
        根据ID获取课程对象
        """
        with db_manager as db:
            result = db.fetch_one(
                'SELECT id, name, teacher_id, class_name, course_type, start_time, end_time FROM courses WHERE id=?',
                (course_id,)
            )
            if result:
                return cls(
                    id=result[0],
                    name=result[1],
                    teacher_id=result[2],
                    class_name=result[3],
                    course_type=result[4],
                    start_time=result[5],
                    end_time=result[6]
                )
            return None
    
    @classmethod
    def get_all(cls):
        """
        获取所有课程
        """
        with db_manager as db:
            results = db.fetch_all(
                'SELECT id, name, teacher_id, class_name, course_type, start_time, end_time FROM courses ORDER BY start_time'
            )
            return [cls(
                id=row[0],
                name=row[1],
                teacher_id=row[2],
                class_name=row[3],
                course_type=row[4],
                start_time=row[5],
                end_time=row[6]
            ) for row in results]
    
    @classmethod
    def get_by_time_range(cls, start_time, end_time):
        """
        获取指定时间范围内的课程
        """
        with db_manager as db:
            results = db.fetch_all(
                '''
                SELECT id, name, teacher_id, class_name, course_type, start_time, end_time 
                FROM courses 
                WHERE start_time < ? AND end_time > ? 
                ORDER BY start_time
                ''',
                (end_time, start_time)
            )
            return [cls(
                id=row[0],
                name=row[1],
                teacher_id=row[2],
                class_name=row[3],
                course_type=row[4],
                start_time=row[5],
                end_time=row[6]
            ) for row in results]
    
    @classmethod
    def get_by_teacher(cls, teacher_id):
        """
        获取指定教师的课程
        """
        with db_manager as db:
            results = db.fetch_all(
                '''
                SELECT id, name, teacher_id, class_name, course_type, start_time, end_time 
                FROM courses 
                WHERE teacher_id=? 
                ORDER BY start_time
                ''',
                (teacher_id,)
            )
            return [cls(
                id=row[0],
                name=row[1],
                teacher_id=row[2],
                class_name=row[3],
                course_type=row[4],
                start_time=row[5],
                end_time=row[6]
            ) for row in results]

# 测试函数
def test_course_model():
    """
    测试课程模型
    """
    from .teacher import Teacher
    from .student import Student
    
    # 创建测试教师
    teacher = Teacher(name='张老师', contact='13900139000', subject_types='数学,物理')
    teacher_id = teacher.save()
    
    # 创建测试学生
    student = Student(name='张三', contact='13800138000', tags='数学班')
    student_id = student.save()
    
    # 创建测试课程
    course = Course(
        name='数学课',
        teacher_id=teacher_id,
        class_name='高一数学班',
        course_type='数学',
        start_time='2024-01-15 09:00',
        end_time='2024-01-15 10:30'
    )
    
    try:
        course_id = course.save()
        print(f"创建课程成功，ID: {course_id}")
        
        # 添加学生
        course.add_student(student_id)
        students = course.get_students()
        print(f"课程学生: {students}")
        
        # 检查时间冲突
        conflict_course = Course(
            name='冲突课程',
            teacher_id=teacher_id,
            class_name='高一数学班',
            course_type='数学',
            start_time='2024-01-15 09:30',
            end_time='2024-01-15 11:00'
        )
        
        try:
            conflict_course.save()
            print("时间冲突检测失败！")
        except Exception as e:
            print(f"时间冲突检测成功: {e}")
        
    finally:
        # 清理测试数据
        if 'course' in locals() and course.id:
            course.delete()
        if 'student' in locals() and student.id:
            student.delete()
        if 'teacher' in locals() and teacher.id:
            teacher.delete()
        print("测试完成")

if __name__ == "__main__":
    test_course_model()