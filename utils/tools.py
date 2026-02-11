import csv
import json
from datetime import datetime

def read_csv_file(file_path):
    """
    读取CSV文件
    """
    data = []
    try:
        with open(file_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    except Exception as e:
        print(f"读取CSV文件失败: {e}")
    return data

def write_csv_file(file_path, data, headers):
    """
    写入CSV文件
    """
    try:
        with open(file_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)
        return True
    except Exception as e:
        print(f"写入CSV文件失败: {e}")
        return False

def parse_time_string(time_str):
    """
    解析时间字符串
    """
    try:
        return datetime.strptime(time_str, '%Y-%m-%d %H:%M')
    except Exception as e:
        print(f"解析时间失败: {e}")
        return None

def format_time_string(dt):
    """
    格式化时间为字符串
    """
    if dt:
        return dt.strftime('%Y-%m-%d %H:%M')
    return ''

def check_time_overlap(start1, end1, start2, end2):
    """
    检查两个时间区间是否重叠
    """
    # 解析时间
    s1 = parse_time_string(start1)
    e1 = parse_time_string(end1)
    s2 = parse_time_string(start2)
    e2 = parse_time_string(end2)
    
    if not all([s1, e1, s2, e2]):
        return False
    
    # 检查重叠
    return (s1 < e2) and (s2 < e1)

def generate_time_slots(start_time, end_time, duration=60):
    """
    生成时间槽
    """
    slots = []
    current = parse_time_string(start_time)
    end = parse_time_string(end_time)
    
    if not all([current, end]):
        return slots
    
    import datetime as dt
    delta = dt.timedelta(minutes=duration)
    
    while current < end:
        slot_end = current + delta
        if slot_end > end:
            break
        slots.append({
            'start': current.strftime('%Y-%m-%d %H:%M'),
            'end': slot_end.strftime('%Y-%m-%d %H:%M')
        })
        current = slot_end
    
    return slots

def export_data_to_json(data, file_path):
    """
    导出数据到JSON文件
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"导出JSON失败: {e}")
        return False

def import_data_from_json(file_path):
    """
    从JSON文件导入数据
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"导入JSON失败: {e}")
        return None

def validate_student_data(data):
    """
    验证学生数据
    """
    required_fields = ['姓名']
    for item in data:
        for field in required_fields:
            if field not in item or not item[field]:
                return False, f'缺少必填字段: {field}'
    return True, '验证通过'

def validate_teacher_data(data):
    """
    验证教师数据
    """
    required_fields = ['姓名']
    for item in data:
        for field in required_fields:
            if field not in item or not item[field]:
                return False, f'缺少必填字段: {field}'
    return True, '验证通过'

def validate_course_data(data):
    """
    验证课程数据
    """
    required_fields = ['课程名称', '教师姓名', '开始时间', '结束时间']
    for item in data:
        for field in required_fields:
            if field not in item or not item[field]:
                return False, f'缺少必填字段: {field}'
    return True, '验证通过'

if __name__ == '__main__':
    # 测试工具函数
    print("测试工具函数")
    
    # 测试时间解析
    time_str = '2024-01-15 09:00'
    dt = parse_time_string(time_str)
    print(f"解析时间: {dt}")
    
    # 测试时间格式化
    if dt:
        formatted = format_time_string(dt)
        print(f"格式化时间: {formatted}")
    
    # 测试时间重叠检测
    start1 = '2024-01-15 09:00'
    end1 = '2024-01-15 10:30'
    start2 = '2024-01-15 10:00'
    end2 = '2024-01-15 11:30'
    overlap = check_time_overlap(start1, end1, start2, end2)
    print(f"时间重叠: {overlap}")
    
    # 测试时间槽生成
    slots = generate_time_slots('2024-01-15 09:00', '2024-01-15 12:00', 60)
    print(f"生成时间槽: {len(slots)}个")
    for slot in slots:
        print(f"  {slot['start']} - {slot['end']}")