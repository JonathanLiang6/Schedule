from database import db_manager

class Textbook:
    """
    教材模型类
    """
    
    def __init__(self, id=None, name='', price=0.0, description=''):
        """
        初始化教材对象
        """
        self.id = id
        self.name = name
        self.price = price
        self.description = description
    
    def save(self):
        """
        保存教材信息到数据库
        """
        with db_manager as db:
            if self.id is None:
                # 新增教材
                db.execute(
                    'INSERT INTO textbooks (name, price, description) VALUES (?, ?, ?)',
                    (self.name, self.price, self.description)
                )
                self.id = db.get_last_insert_id()
            else:
                # 更新教材信息
                db.execute(
                    'UPDATE textbooks SET name=?, price=?, description=? WHERE id=?',
                    (self.name, self.price, self.description, self.id)
                )
        return self.id
    
    def delete(self):
        """
        从数据库中删除教材
        """
        if self.id:
            with db_manager as db:
                # 先删除关联数据
                db.execute('DELETE FROM student_textbooks WHERE textbook_id=?', (self.id,))
                # 删除教材
                db.execute('DELETE FROM textbooks WHERE id=?', (self.id,))
    
    def get_students(self):
        """
        获取使用该教材的学生
        """
        if self.id:
            with db_manager as db:
                result = db.fetch_all(
                    '''
                    SELECT s.id, s.name FROM students s
                    JOIN student_textbooks st ON s.id = st.student_id
                    WHERE st.textbook_id=?
                    ''',
                    (self.id,)
                )
                return result
        return []
    
    def get_issued_count(self):
        """
        获取已发放的数量
        """
        if self.id:
            with db_manager as db:
                result = db.fetch_one(
                    'SELECT COUNT(*) FROM student_textbooks WHERE textbook_id=? AND is_issued=1',
                    (self.id,)
                )
                return result[0] if result else 0
        return 0
    
    def get_total_count(self):
        """
        获取总使用数量
        """
        if self.id:
            with db_manager as db:
                result = db.fetch_one(
                    'SELECT COUNT(*) FROM student_textbooks WHERE textbook_id=?',
                    (self.id,)
                )
                return result[0] if result else 0
        return 0
    
    def get_total_cost(self):
        """
        获取总费用
        """
        return self.price * self.get_total_count()
    
    @classmethod
    def get_by_id(cls, textbook_id):
        """
        根据ID获取教材对象
        """
        with db_manager as db:
            result = db.fetch_one('SELECT id, name, price, description FROM textbooks WHERE id=?', (textbook_id,))
            if result:
                return cls(id=result[0], name=result[1], price=result[2], description=result[3])
            return None
    
    @classmethod
    def get_all(cls):
        """
        获取所有教材
        """
        with db_manager as db:
            results = db.fetch_all('SELECT id, name, price, description FROM textbooks ORDER BY name')
            return [cls(id=row[0], name=row[1], price=row[2], description=row[3]) for row in results]
    
    @classmethod
    def search_by_name(cls, name):
        """
        根据名称搜索教材
        """
        with db_manager as db:
            results = db.fetch_all(
                'SELECT id, name, price, description FROM textbooks WHERE name LIKE ? ORDER BY name',
                (f'%{name}%',)
            )
            return [cls(id=row[0], name=row[1], price=row[2], description=row[3]) for row in results]
    
    @classmethod
    def get_statistics(cls):
        """
        获取教材统计信息
        """
        with db_manager as db:
            query = '''
            SELECT t.id, t.name, t.price, 
                   COUNT(st.student_id) as total_count,
                   SUM(CASE WHEN st.is_issued=1 THEN 1 ELSE 0 END) as issued_count,
                   t.price * COUNT(st.student_id) as total_cost
            FROM textbooks t
            LEFT JOIN student_textbooks st ON t.id = st.textbook_id
            GROUP BY t.id, t.name, t.price
            ORDER BY t.name
            '''
            return db.fetch_all(query)

# 测试函数
def test_textbook_model():
    """
    测试教材模型
    """
    from .student import Student
    
    # 创建测试教材
    textbook = Textbook(name='数学必修一', price=50.0, description='高中数学必修教材')
    textbook_id = textbook.save()
    print(f"创建教材成功，ID: {textbook_id}")
    
    # 创建测试学生
    student1 = Student(name='张三', contact='13800138000', tags='数学班')
    student1_id = student1.save()
    
    student2 = Student(name='李四', contact='13800138001', tags='数学班')
    student2_id = student2.save()
    
    # 为学生添加教材
    student1.add_textbook(textbook_id, 1)  # 已发放
    student2.add_textbook(textbook_id, 0)  # 未发放
    
    # 获取使用该教材的学生
    students = textbook.get_students()
    print(f"使用该教材的学生: {[s[1] for s in students]}")
    
    # 获取统计信息
    issued_count = textbook.get_issued_count()
    total_count = textbook.get_total_count()
    total_cost = textbook.get_total_cost()
    print(f"已发放: {issued_count}, 总数: {total_count}, 总费用: {total_cost}")
    
    # 获取所有教材统计
    statistics = Textbook.get_statistics()
    print("教材统计:")
    for stat in statistics:
        print(f"{stat[1]}: 单价={stat[2]}, 使用人数={stat[3]}, 已发放={stat[4]}, 总费用={stat[5]}")
    
    # 清理测试数据
    student1.delete()
    student2.delete()
    textbook.delete()
    print("测试完成")

if __name__ == "__main__":
    test_textbook_model()