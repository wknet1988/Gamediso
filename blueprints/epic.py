from flask import Blueprint, request, jsonify
import time
import json
import os
from epic_db import clear_epic_games, upsert_epic_game, get_epic_auth
from cache_manager import download_platform_image
from epic_client import fetch_epic_games, is_epic_authenticated, get_epic_account_name
from core.config import config

epic_bp = Blueprint('epic', __name__, url_prefix='/api/epic')

# 配置目录（与旧版保持一致）
LEGENDARY_CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'legendary_config')
os.makedirs(LEGENDARY_CONFIG_DIR, exist_ok=True)

def run_legendary(args):
    # 此函数已在 epic_client 中定义，但这里为保持独立，可重新导入或直接调用 epic_client 中的函数
    from epic_client import run_legendary
    return run_legendary(args, LEGENDARY_CONFIG_DIR)

@epic_bp.route('/login')
def epic_login():
    return jsonify({"login_url": "https://legendary.gl/epiclogin"})

@epic_bp.route('/auth_code', methods=['POST'])
def epic_auth_code():
    data = request.json
    code = data.get('code')
    if not code:
        return jsonify({"success": False, "error": "Missing code"}), 400
    from epic_client import run_legendary
    result = run_legendary(["auth", "--code", code], LEGENDARY_CONFIG_DIR)
    if result.returncode != 0:
        return jsonify({"success": False, "error": result.stderr}), 400
    if is_epic_authenticated():
        return jsonify({"success": True, "account_name": get_epic_account_name()})
    else:
        return jsonify({"success": False, "error": "Authentication failed"}), 400

@epic_bp.route('/status')
def epic_status():
    if is_epic_authenticated():
        return jsonify({"authenticated": True, "account_name": get_epic_account_name()})
    return jsonify({"authenticated": False})

@epic_bp.route('/sync', methods=['POST'])
def sync_epic_library():
    if not is_epic_authenticated():
        return jsonify({"success": False, "error": "Not logged in"}), 401

    # 使用新的 fetch_epic_games（内部会调用 info 获取封面）
    from epic_client import fetch_epic_games
    games = fetch_epic_games(None, LEGENDARY_CONFIG_DIR)  # access_token 不需要，因为使用 config_dir 中的凭证

    clear_epic_games()
    now = int(time.time())
    for game in games:
        app_name = game['game_id']
        title = game['name']
        cover_url = game['header_url']
        if cover_url:
            download_platform_image(cover_url, 'epic', app_name)
        upsert_epic_game(app_name, title, cover_url, app_name, now)

    return jsonify({"success": True, "count": len(games)})