#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库连接和数据检查脚本
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'server_python'))

from server_python.database.database import get_connection, init_detect_result_table

def test_database():
    """测试数据库连接和数据"""
    print("正在测试数据库连接...")

    # 测试连接
    connection = get_connection()
    if not connection:
        print("❌ 数据库连接失败")
        return False

    print("✅ 数据库连接成功")

    try:
        cursor = connection.cursor()

        # 检查表是否存在
        cursor.execute("SHOW TABLES LIKE 'detect_result'")
        table_exists = cursor.fetchone()

        if not table_exists:
            print("⚠️  detect_result表不存在，正在创建...")
            init_detect_result_table()
        else:
            print("✅ detect_result表存在")

        # 查询数据总数
        cursor.execute("SELECT COUNT(*) FROM detect_result")
        total = cursor.fetchone()[0]
        print(f"📊 数据库中共有 {total} 条检测记录")

        if total > 0:
            # 查询最近的几条记录
            cursor.execute("""
                SELECT id, detection_type, file_name, create_time
                FROM detect_result
                ORDER BY create_time DESC
                LIMIT 5
            """)
            recent_records = cursor.fetchall()

            print("📝 最近的5条记录：")
            for record in recent_records:
                print(f"   ID: {record[0]}, 类型: {record[1]}, 文件: {record[2]}, 时间: {record[3]}")
        else:
            print("⚠️  数据库中没有检测记录")
            print("💡 请先进行一次图像或视频检测来生成数据")

        # 检查索引
        cursor.execute("SHOW INDEX FROM detect_result")
        indexes = cursor.fetchall()
        print(f"📋 表索引数量: {len(indexes)}")

        return True

    except Exception as e:
        print(f"❌ 数据库操作失败: {e}")
        return False
    finally:
        connection.close()

if __name__ == "__main__":
    test_database()