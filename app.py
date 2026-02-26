# -*- coding: utf-8 -*-
"""
花名查重系统
功能：新人入职取花名时进行查重检测
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime

app = Flask(__name__)

# 使用内存存储（Render 免费版不支持持久化存储）
# 注意：服务重启后数据会丢失
flower_names_db = {}  # {'name': {'name': '花名', 'created_at': timestamp}}


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
        'names': names
    })


@app.route('/api/batch-add', methods=['POST'])
def batch_add():
    """批量添加花名API"""
    data = request.get_json()
    names = data.get('names', [])
    
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)