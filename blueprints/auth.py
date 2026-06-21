from flask import Blueprint, request, jsonify, session, redirect
from core.config import config, save_config
from steam_client import get_steam_login_url, validate_steam_callback
from core.task_manager import task_manager
import os
import threading
import uuid

auth_bp = Blueprint('auth', __name__, url_prefix='/api')

@auth_bp.route('/login')
def api_login():
    return_to = request.url_root.rstrip('/') + '/api/auth'
    login_url = get_steam_login_url(return_to)
    return jsonify({"login_url": login_url})

@auth_bp.route('/auth')
def api_auth():
    callback_url = request.url
    steamid = validate_steam_callback(callback_url)
    if steamid:
        session['steamid'] = steamid
        config['steamid'] = steamid
        save_config(config)
        return redirect('/')
    else:
        return "登录失败", 400

@auth_bp.route('/status')
def api_status():
    if not session.get('steamid') and config.get('steamid'):
        session['steamid'] = config['steamid']
    if not session.get('api_key') and config.get('api_key'):
        session['api_key'] = config['api_key']
    if not session.get('steam_path') and config.get('steam_path'):
        session['steam_path'] = config['steam_path']

    steamid = session.get('steamid')
    api_key = session.get('api_key')
    steam_path = session.get('steam_path')
    if steamid and api_key and steam_path:
        return jsonify({"logged_in": True, "steamid": steamid, "has_steam_path": True})
    elif steamid and api_key:
        return jsonify({"logged_in": False, "steamid": steamid, "need_steam_path": True})
    elif steamid:
        return jsonify({"logged_in": False, "steamid": steamid, "need_api_key": True})
    else:
        return jsonify({"logged_in": False})

@auth_bp.route('/set_api_key', methods=['POST'])
def api_set_api_key():
    data = request.json
    api_key = data.get('api_key')
    if api_key:
        session['api_key'] = api_key
        config['api_key'] = api_key
        save_config(config)
        # 触发 Steam 游戏库同步
        from steam_client import refresh_games_library
        steamid = session.get('steamid') or config.get('steamid')
        steam_path = session.get('steam_path') or config.get('steam_path')
        refresh_games_library(steamid, api_key, steam_path, force=True)
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@auth_bp.route('/set_steam_path', methods=['POST'])
def api_set_steam_path():
    data = request.json
    steam_path = data.get('steam_path')
    if steam_path and os.path.exists(steam_path):
        session['steam_path'] = steam_path
        config['steam_path'] = steam_path
        save_config(config)
        # 刷新 Steam 自定义列表
        from steam_client import refresh_shelves_from_steam
        steamid = session.get('steamid') or config.get('steamid')
        refresh_shelves_from_steam(steam_path, steamid)
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "路径无效"}), 400

@auth_bp.route('/init_library', methods=['POST'])
def api_init_library():
    steamid = session.get('steamid') or config.get('steamid')
    api_key = session.get('api_key') or config.get('api_key')
    steam_path = session.get('steam_path') or config.get('steam_path')

    if not steamid or not api_key:
        return jsonify({"success": False, "error": "Missing credentials"}), 400

    task_id = str(uuid.uuid4())
    task_manager.create_task(task_id, 100)

    # 在后台线程执行同步
    def run_sync():
        from steam_client import refresh_games_library
        refresh_games_library(steamid, api_key, steam_path, force=True, task_id=task_id)

    thread = threading.Thread(target=run_sync)
    thread.daemon = True
    thread.start()

    return jsonify({"task_id": task_id})

@auth_bp.route('/task/<task_id>')
def get_task_status(task_id):
    status = task_manager.get_task(task_id)
    if not status:
        return jsonify({"error": "Task not found"}), 404
    return jsonify(status)

@auth_bp.route('/alt/login')
def api_alt_login():
    return_to = request.url_root.rstrip('/') + '/api/alt/auth'
    login_url = get_steam_login_url(return_to)
    return jsonify({"login_url": login_url})

@auth_bp.route('/alt/auth')
def api_alt_auth():
    callback_url = request.url
    steamid = validate_steam_callback(callback_url)
    if steamid:
        session['steamid_alt'] = steamid
        config['steamid_alt'] = steamid
        save_config(config)
        return redirect('/')
    else:
        return "登录失败", 400

@auth_bp.route('/alt/status')
def api_alt_status():
    steamid = session.get('steamid_alt') or config.get('steamid_alt')
    api_key = session.get('api_key_alt') or config.get('api_key_alt')
    if steamid and api_key:
        return jsonify({"logged_in": True, "steamid": steamid})
    elif steamid:
        return jsonify({"logged_in": False, "need_api_key": True})
    else:
        return jsonify({"logged_in": False})

@auth_bp.route('/alt/set_api_key', methods=['POST'])
def api_set_alt_api_key():
    data = request.json
    api_key = data.get('api_key')
    if api_key:
        session['api_key_alt'] = api_key
        config['api_key_alt'] = api_key
        save_config(config)
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@auth_bp.route('/alt/init_library', methods=['POST'])
def api_init_alt_library():
    steamid = session.get('steamid_alt') or config.get('steamid_alt')
    api_key = session.get('api_key_alt') or config.get('api_key_alt')
    if not steamid or not api_key:
        return jsonify({"success": False, "error": "Missing credentials"}), 400

    task_id = str(uuid.uuid4())
    task_manager.create_task(task_id, 100)

    def run_sync():
        from steam_client import refresh_games_library_alt
        refresh_games_library_alt(steamid, api_key, force=True, task_id=task_id)

    thread = threading.Thread(target=run_sync)
    thread.daemon = True
    thread.start()

    return jsonify({"task_id": task_id})

@auth_bp.route('/set_steamgriddb_api_key', methods=['POST'])
def set_steamgriddb_api_key():
    data = request.json
    api_key = data.get('api_key', '').strip()
    if not api_key:
        return jsonify({"success": False, "error": "API Key cannot be empty"}), 400
    config['steamgriddb_api_key'] = api_key
    save_config(config)
    return jsonify({"success": True})