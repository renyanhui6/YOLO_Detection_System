import os
import pymysql
import json
from datetime import datetime
from typing import Optional

def _load_env():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    env_path = os.path.join(root_dir, '.env')
    if not os.path.isfile(env_path):
        return
    try:
        with open(env_path, 'r', encoding='utf-8') as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception as e:
        print(f"加载.env失败: {e}")

_load_env()

def _load_db_config():
    """从环境变量读取数据库配置，提供默认值便于本地调试"""
    return {
        'user': os.environ.get('DB_USER', 'root'),
        'host': os.environ.get('DB_HOST', '127.0.0.1'),
        'password': os.environ.get('DB_PASSWORD', '45987530'),
        'db': os.environ.get('DB_NAME', 'yolo_database'),
        'port': int(os.environ.get('DB_PORT', '3306')),
        'charset': os.environ.get('DB_CHARSET', 'utf8mb4')
    }

# 数据库连接配置
DB_CONFIG = _load_db_config()

def get_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(**DB_CONFIG)
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def init_detect_result_table():
    """初始化detect_result表"""
    connection = get_connection()
    if not connection:
        return False

    try:
        cursor = connection.cursor()

        # 仅在不存在时创建detect_result表（不会清空已有数据）
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS detect_result (
            id INT AUTO_INCREMENT PRIMARY KEY,
            detection_type ENUM('image', 'video') NOT NULL COMMENT '检测类型',
            file_name VARCHAR(255) NOT NULL COMMENT '文件名',
            file_path VARCHAR(500) COMMENT '文件路径',
            detection_result JSON NOT NULL COMMENT '检测结果JSON',
            object_count INT DEFAULT 0 COMMENT '检测到的对象数量',
            confidence_avg FLOAT DEFAULT 0 COMMENT '平均置信度',
            processing_time FLOAT DEFAULT 0 COMMENT '处理时间(秒)',
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
            INDEX idx_create_time (create_time),
            INDEX idx_detection_type (detection_type),
            INDEX idx_type_time (detection_type, create_time)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='YOLO检测结果表'
        """

        cursor.execute(create_table_sql)

        # 为已存在的表添加索引（如果不存在）
        try:
            cursor.execute("ALTER TABLE detect_result ADD INDEX idx_create_time (create_time)")
        except:
            pass  # 索引可能已存在

        try:
            cursor.execute("ALTER TABLE detect_result ADD INDEX idx_detection_type (detection_type)")
        except:
            pass  # 索引可能已存在

        try:
            cursor.execute("ALTER TABLE detect_result ADD INDEX idx_type_time (detection_type, create_time)")
        except:
            pass  # 索引可能已存在
        connection.commit()
        print("detect_result表检查/创建成功")
        return True
        
    except Exception as e:
        print(f"创建表失败: {e}")
        return False
    finally:
        connection.close()

def init_knowledge_table():
    """初始化knowledge表"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        
        # 创建knowledge表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS knowledge (
            id INT AUTO_INCREMENT PRIMARY KEY,
            label_name VARCHAR(255) NOT NULL COMMENT '知识条目标题',
            label_desc TEXT COMMENT '知识条目描述/内容',
            category VARCHAR(100) DEFAULT '未分类' COMMENT '知识分类',
            keywords TEXT COMMENT '关键词，JSON格式存储',
            create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
            update_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='知识库表'
        """
        
        cursor.execute(create_table_sql)
        connection.commit()
        print("knowledge表检查/创建成功")
        return True
        
    except Exception as e:
        print(f"创建knowledge表失败: {e}")
        return False
    finally:
        connection.close()

def save_detection_result(detection_type, file_name, file_path, detection_result, processing_time=0):
    """保存检测结果到数据库"""
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        
        # 计算统计信息
        object_count = 0
        confidence_sum = 0
        confidence_count = 0
        
        if detection_type == 'image' and 'objects' in detection_result:
            object_count = len(detection_result['objects'])
            for obj in detection_result['objects']:
                if 'confidence' in obj:
                    confidence_sum += obj['confidence']
                    confidence_count += 1
        elif detection_type == 'video' and 'frames' in detection_result:
            for frame in detection_result['frames']:
                if 'objects' in frame:
                    object_count += len(frame['objects'])
                    for obj in frame['objects']:
                        if 'confidence' in obj:
                            confidence_sum += obj['confidence']
                            confidence_count += 1
        
        confidence_avg = confidence_sum / confidence_count if confidence_count > 0 else 0
        
        # 插入数据
        insert_sql = """
        INSERT INTO detect_result 
        (detection_type, file_name, file_path, detection_result, object_count, confidence_avg, processing_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        
        cursor.execute(insert_sql, (
            detection_type,
            file_name,
            file_path,
            json.dumps(detection_result, ensure_ascii=False),
            object_count,
            confidence_avg,
            processing_time
        ))
        
        connection.commit()
        result_id = cursor.lastrowid
        print(f"检测结果保存成功，ID: {result_id}")
        return result_id
        
    except Exception as e:
        print(f"保存检测结果失败: {e}")
        return None
    finally:
        connection.close()

def query_detection_results(page=1, page_size=10, detection_type=None, sort_order='desc', order_by='create_time'):
    """查询检测结果"""
    connection = get_connection()
    if not connection:
        return None

    try:
        cursor = connection.cursor()

        # 构建查询条件
        where_clause = ""
        params = []
        if detection_type:
            where_clause = "WHERE detection_type = %s"
            params.append(detection_type)

        # 查询总数
        count_sql = f"SELECT COUNT(*) FROM detect_result {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]

        # 如果没有数据，直接返回空结果
        if total == 0:
            return {
                'data': [],
                'total': 0,
                'page': page,
                'page_size': page_size,
                'total_pages': 0
            }

        # 构建排序子句 - 使用ID作为备用排序以确保稳定性
        valid_columns = ['create_time', 'update_time', 'id', 'file_name']
        valid_orders = ['asc', 'desc']

        if order_by not in valid_columns:
            order_by = 'create_time'
        if sort_order.lower() not in valid_orders:
            sort_order = 'desc'

        # 为了避免排序缓冲区问题，限制排序字段并添加ID作为次要排序
        if order_by == 'create_time':
            order_clause = f"ORDER BY create_time {sort_order.upper()}, id {sort_order.upper()}"
        else:
            order_clause = f"ORDER BY {order_by} {sort_order.upper()}, id {sort_order.upper()}"

        # 限制最大查询数量
        if page_size > 1000:
            page_size = 1000

        # 分页查询
        offset = (page - 1) * page_size
        query_sql = f"""
        SELECT id, detection_type, file_name, file_path, detection_result,
               object_count, confidence_avg, processing_time, create_time, update_time
        FROM detect_result {where_clause}
        {order_clause}
        LIMIT %s OFFSET %s
        """

        params.extend([page_size, offset])
        cursor.execute(query_sql, params)
        results = cursor.fetchall()
        
        # 封装数据
        data = []
        for result in results:
            item = {
                'id': result[0],
                'detection_type': result[1],
                'file_name': result[2],
                'file_path': result[3],
                'detection_result': json.loads(result[4]) if result[4] else {},
                'object_count': result[5],
                'confidence_avg': result[6],
                'processing_time': result[7],
                'create_time': result[8].strftime('%Y-%m-%d %H:%M:%S') if result[8] else None,
                'update_time': result[9].strftime('%Y-%m-%d %H:%M:%S') if result[9] else None
            }
            data.append(item)
        
        return {
            'data': data,
            'total': total,
            'page': page,
            'page_size': page_size,
            'total_pages': (total + page_size - 1) // page_size
        }
        
    except Exception as e:
        print(f"查询检测结果失败: {e}")
        return None
    finally:
        connection.close()

def delete_detection_result(result_id):
    """删除检测结果"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        delete_sql = "DELETE FROM detect_result WHERE id = %s"
        cursor.execute(delete_sql, (result_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"检测结果删除成功，ID: {result_id}")
            return True
        else:
            print(f"未找到要删除的记录，ID: {result_id}")
            return False
            
    except Exception as e:
        print(f"删除检测结果失败: {e}")
        return False
    finally:
        connection.close()

# 从数据库中获取知识库数据，封装成json
def query_knowledge(search: Optional[str] = None, category: Optional[str] = None):
    """查询知识库数据，支持按关键字和分类搜索，并将结果转换为前端所需结构"""
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor()
        
        base_sql = 'SELECT id, label_name, label_desc, category, keywords, create_time, update_time FROM knowledge'
        params = []
        conditions = []
        
        if search and search.strip():
            like = f"%{search.strip()}%"
            conditions.append('(label_name LIKE %s OR label_desc LIKE %s)')
            params.extend([like, like])
        
        if category and category.strip():
            conditions.append('category = %s')
            params.append(category.strip())
        
        if conditions:
            base_sql += ' WHERE ' + ' AND '.join(conditions)
        
        base_sql += ' ORDER BY update_time DESC'
        
        cursor.execute(base_sql, params)
        results = cursor.fetchall()
        
        final = []
        for result in results:
            kid, name, desc, cat, keywords_str, ctime, utime = result
            
            # 解析关键词
            keywords = []
            if keywords_str:
                try:
                    keywords = json.loads(keywords_str) if isinstance(keywords_str, str) else keywords_str
                except:
                    keywords = []
            
            item = {
                'id': kid,
                'title': name or '',
                'category': cat or '未分类',
                'summary': desc[:100] + '...' if desc and len(desc) > 100 else (desc or ''),
                'content': desc or '',
                'keywords': keywords if isinstance(keywords, list) else [],
                'updateTime': utime.strftime('%Y-%m-%dT%H:%M:%S') if utime else (ctime.strftime('%Y-%m-%dT%H:%M:%S') if ctime else None)
            }
            final.append(item)
        
        return final
        
    except Exception as e:
        print(f"查询知识库失败: {e}")
        return []
    finally:
        connection.close()


def add_knowledge(title: str, content: str, category: str = '未分类', keywords: list = None) -> bool:
    """添加知识库记录"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        keywords_json = json.dumps(keywords or [], ensure_ascii=False)
        
        sql = '''
        INSERT INTO knowledge (label_name, label_desc, category, keywords)
        VALUES (%s, %s, %s, %s)
        '''
        cursor.execute(sql, (title, content, category, keywords_json))
        connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"添加知识库失败: {e}")
        return False
    finally:
        connection.close()


def update_knowledge(knowledge_id: int, title: str, content: str, category: str = '未分类', keywords: list = None) -> bool:
    """更新知识库记录"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        keywords_json = json.dumps(keywords or [], ensure_ascii=False)
        
        sql = '''
        UPDATE knowledge 
        SET label_name = %s, label_desc = %s, category = %s, keywords = %s, update_time = CURRENT_TIMESTAMP
        WHERE id = %s
        '''
        cursor.execute(sql, (title, content, category, keywords_json, knowledge_id))
        connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"更新知识库失败: {e}")
        return False
    finally:
        connection.close()


def get_knowledge_by_id(knowledge_id: int):
    """根据ID获取知识库记录"""
    connection = get_connection()
    if not connection:
        return None
    
    try:
        cursor = connection.cursor()
        sql = 'SELECT id, label_name, label_desc, category, keywords, create_time, update_time FROM knowledge WHERE id = %s'
        cursor.execute(sql, (knowledge_id,))
        result = cursor.fetchone()
        
        if result:
            kid, name, desc, cat, keywords_str, ctime, utime = result
            
            # 解析关键词
            keywords = []
            if keywords_str:
                try:
                    keywords = json.loads(keywords_str) if isinstance(keywords_str, str) else keywords_str
                except:
                    keywords = []
            
            return {
                'id': kid,
                'title': name or '',
                'category': cat or '未分类',
                'summary': desc[:100] + '...' if desc and len(desc) > 100 else (desc or ''),
                'content': desc or '',
                'keywords': keywords if isinstance(keywords, list) else [],
                'updateTime': utime.strftime('%Y-%m-%dT%H:%M:%S') if utime else (ctime.strftime('%Y-%m-%dT%H:%M:%S') if ctime else None)
            }
        
        return None
        
    except Exception as e:
        print(f"查询知识库记录失败: {e}")
        return None
    finally:
        connection.close()


def get_knowledge_categories():
    """获取所有知识分类"""
    connection = get_connection()
    if not connection:
        return []
    
    try:
        cursor = connection.cursor()
        sql = 'SELECT DISTINCT category FROM knowledge WHERE category IS NOT NULL ORDER BY category'
        cursor.execute(sql)
        results = cursor.fetchall()
        
        categories = [row[0] for row in results if row[0]]
        return categories
        
    except Exception as e:
        print(f"获取知识分类失败: {e}")
        return []
    finally:
        connection.close()


def delete_knowledge(knowledge_id: int) -> bool:
    """删除知识库记录"""
    connection = get_connection()
    if not connection:
        return False
    
    try:
        cursor = connection.cursor()
        sql = 'DELETE FROM knowledge WHERE id = %s'
        cursor.execute(sql, (knowledge_id,))
        connection.commit()
        return cursor.rowcount > 0
    except Exception as e:
        print(f"删除知识库失败: {e}")
        return False
    finally:
        connection.close()

# 初始化数据库表
if __name__ == "__main__":
    init_detect_result_table()
    init_knowledge_table()
    print("数据库初始化完成")
