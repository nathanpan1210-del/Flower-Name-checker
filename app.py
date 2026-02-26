# -*- coding: utf-8 -*-
"""
花名查重系统
功能：新人入职取花名时进行查重检测
"""

import sqlite3
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
DB_NAME = "flower_names.db"


def init_db():
    """初始化数据库，创建花名表"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS flower_names (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


def add_flower_name(name):
    """添加花名到数据库"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO flower_names (name) VALUES (?)", (name,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def check_flower_name(name):
    """检查花名是否存在"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, created_at FROM flower_names WHERE name = ?", (name,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def get_all_names():
    """获取所有已使用的花名（用于管理）"""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT name, created_at FROM flower_names ORDER BY created_at DESC")
    results = cursor.fetchall()
    conn.close()
    return results


@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')


@app.route('/api/check', methods=['POST'])
def check():
    """查重API"""
    data = request.get_json()
    name = data.get('name', '').strip().lower()
    
    if not name:
        return jsonify({'success': False, 'message': '请输入花名'})
    
    exists = check_flower_name(name)
    
    if exists:
        return jsonify({
            'success': True,
            'available': False,
            'message': '❌ 花名已被占用，请选择其他名字'
        })
    else:
        return jsonify({
            'success': True,
            'available': True,
            'message': '✅ 花名可用！'
        })


@app.route('/api/add', methods=['POST'])
def add():
    """添加花名API"""
    data = request.get_json()
    name = data.get('name', '').strip().lower()
    
    if not name:
        return jsonify({'success': False, 'message': '请输入花名'})
    
    if add_flower_name(name):
        return jsonify({
            'success': True,
            'message': '✅ 花名添加成功！'
        })
    else:
        return jsonify({
            'success': False,
            'message': '❌ 花名已存在，添加失败'
        })


@app.route('/api/list', methods=['GET'])
def list_names():
    """获取所有已使用的花名"""
    names = get_all_names()
    return jsonify({
        'success': True,
        'names': [{'name': n[0], 'created_at': n[1]} for n in names]
    })


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)