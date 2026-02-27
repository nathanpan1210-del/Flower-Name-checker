# -*- coding: utf-8 -*-
"""
花名查重系统
功能：新人入职取花名时进行查重检测
数据存储：飞书 Bitable
"""

from flask import Flask, render_template, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)

# 飞书 Bitable 配置
BITABLE_APP_TOKEN = os.environ.get('BITABLE_APP_TOKEN', 'Mysqbz91aaaqYiszBIfc9AAmnJf')
BITABLE_TABLE_ID = os.environ.get('BITABLE_TABLE_ID', 'tblz9AVdx8lVpqPz')
BITABLE_FIELD_NAME = '花名'  # 花名（用字段名而不是 ID）
BITABLE_FIELD_TIME = '创建时间'  # 创建时间（用字段名而不是 ID）
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin123')


def check_flower_name(name):
    """检查花名是否存在"""
    try:
        res = feishu_bitable_list_records(
            app_token=BITABLE_APP_TOKEN,
            table_id=BITABLE_TABLE_ID
        )
        if res.get('success'):
            for item in res.get('items', []):
                fields = item.get('fields', {})
                if fields.get(BITABLE_FIELD_NAME, '').lower() == name.lower():
                    return True
        return False
    except Exception as e:
        print(f"查询失败: {e}")
        return False


def add_flower_name(name):
    """添加花名到 Bitable"""
    try:
        res = feishu_bitable_create_record(
            app_token=BITABLE_APP_TOKEN,
            table_id=BITABLE_TABLE_ID,
            fields={
                BITABLE_FIELD_NAME: name,
            }
        )
        return res.get('success', False)
    except Exception as e:
        print(f"添加失败: {e}")
        return False


def get_all_names():
    """获取所有已使用的花名"""
    try:
        res = feishu_bitable_list_records(
            app_token=BITABLE_APP_TOKEN,
            table_id=BITABLE_TABLE_ID
        )
        if res.get('success'):
            names = []
            for item in res.get('items', []):
                fields = item.get('fields', {})
                names.append({
                    'name': fields.get(BITABLE_FIELD_NAME, ''),
                    'created_at': fields.get(BITABLE_FIELD_TIME, '')
                })
            return names
        return []
    except Exception as e:
        print(f"获取列表失败: {e}")
        return []


@app.route('/')
def index():
    """渲染主页"""
    return render_template('index.html')


@app.route('/api/check', methods=['POST'])
def check():
    """查重API - 公开接口"""
    data = request.get_json()
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'success': False, 'message': '请输入花名'})
    
    exists = check_flower_name(name)
    
    if exists:
        return jsonify({
            'success': True,
            'available': False,
            'message': '❌ 花名重复，请选择其他名字'
        })
    else:
        return jsonify({
            'success': True,
            'available': True,
            'message': '✅ 花名可用！'
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
        if check_flower_name(name):
            skipped.append(name)
        else:
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


@app.route('/api/debug', methods=['GET'])
def debug():
    """调试接口"""
    import httpx
    
    access_token = os.environ.get('FEISHU_ACCESS_TOKEN', '')
    
    # 测试 API
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{BITABLE_TABLE_ID}/records"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = httpx.get(url, headers=headers, params={"page_size": 100}, timeout=30)
        data = resp.json()
        
        return jsonify({
            "token_set": bool(access_token),
            "token_prefix": access_token[:10] if access_token else "",
            "api_response": data,
            "url": url
        })
    except Exception as e:
        return jsonify({
            "error": str(e)
        })


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)


# 飞书 Bitable API 封装
def feishu_bitable_list_records(app_token, table_id, page_size=100):
    """列出 Bitable 记录"""
    import httpx
    
    # 直接使用 token（临时方案，生产环境建议用环境变量）
    access_token = os.environ.get('FEISHU_ACCESS_TOKEN', '') or 't-g1042r9xNRA3V7R6MVNINUVYI3FLJNMS4W7CZGDN'
    
    if not access_token or access_token == 'your_token_here':
        # 返回模拟数据用于本地测试
        return {'success': True, 'items': []}
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = httpx.get(url, headers=headers, params={"page_size": page_size}, timeout=30)
        data = resp.json()
        if data.get("code") == 0:
            return {"success": True, "items": data.get("data", {}).get("items", [])}
        else:
            print(f"API 错误: {data}")
            return {"success": False, "error": data}
    except Exception as e:
        print(f"请求失败: {e}")
        return {"success": False, "error": str(e)}


def feishu_bitable_create_record(app_token, table_id, fields):
    """创建 Bitable 记录"""
    import httpx
    
    access_token = os.environ.get('FEISHU_ACCESS_TOKEN', '') or 't-g1042r9xNRA3V7R6MVNINUVYI3FLJNMS4W7CZGDN'
    
    if not access_token or access_token == 'your_token_here':
        # 本地测试模式
        return {"success": True}
    
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{app_token}/tables/{table_id}/records"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        resp = httpx.post(url, headers=headers, json={"fields": fields}, timeout=30)
        data = resp.json()
        if data.get("code") == 0:
            return {"success": True}
        else:
            print(f"API 错误: {data}")
            return {"success": False, "error": data}
    except Exception as e:
        print(f"请求失败: {e}")
        return {"success": False, "error": str(e)}