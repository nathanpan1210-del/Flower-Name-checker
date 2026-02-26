# -*- coding: utf-8 -*-
"""
花名查重系统
功能：新人入职取花名时进行查重检测
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# 使用内存存储（Render 免费版不支持持久化存储）
# 注意：服务重启后数据会丢失
flower_names_db = {}  # {'name': {'name': '花名', 'created_at': timestamp}}

# 管理员密码从环境变量读取，默认 admin123
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')


def check_flower_name(name):
    """检查花名是否存在"""
    return name.lower() in flower_names_db


def add_flower_name(name):
    """添加花名到数据库"""
    name_lower = name.lower()
    if name_lower in flower_names_db:
        return False
    flower_names_db[name_lower] = {
        'name': name,
        'created_at': datetime.now().isoformat()
    }
    return True


def get_all_names():
    """获取所有已使用的花名"""
    return sorted(flower_names_db.values(), 
                  key=lambda x: x['created_at'], 
                  reverse=True)


@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')


@app.route('/api/check', methods=['POST'])
def check():
    """查重API - 公开接口"""
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


@app.route('/api/debug', methods=['GET'])
def debug():
    """调试接口 - 查看环境变量是否正确读取"""
    return jsonify({
        'admin_password_read': '***' + ADMIN_PASSWORD[-4:] if ADMIN_PASSWORD else 'None',
        'env_vars': list(os.environ.keys())
    })


@app.route('/api/verify-password', methods=['POST'])
def verify_password():
    """验证密码接口 - 调试用"""
    data = request.get_json()
    input_password = data.get('password', '')
    return jsonify({
        'input_password': input_password,
        'stored_password': '***' + ADMIN_PASSWORD[-4:] if ADMIN_PASSWORD else 'None',
        'match': input_password == ADMIN_PASSWORD
    })


@app.route('/api/batch-add', methods=['POST'])
def batch_add():
    """批量添加花名API - 需要管理员密码"""
    data = request.get_json()
    password = data.get('password', '')
    names = data.get('names', [])
    
    # 验证密码
    if password != ADMIN_PASSWORD:
        return jsonify({'success': False, 'message': '❌ 密码错误'})
    
    if not names:
        return jsonify({'success': False, 'message': '请提供花名列表'})
    
    added = []
    skipped = []
    
    for name in names:
        name = name.strip()
        if not name:
            continue
        if add_flower_name(name):
            added.append(name)
        else:
            skipped.append(name)
    
    return jsonify({
        'success': True,
        'message': f'✅ 成功添加 {len(added)} 个，{len(skipped)} 个已存在',
        'added': added,
        'skipped': skipped
    })


@app.route('/api/list', methods=['GET'])
def list_names():
    """获取所有已使用的花名"""
    names = get_all_names()
    return jsonify({
        'success': True,
        'names': names
    })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)