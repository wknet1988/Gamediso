from flask import Blueprint, request, jsonify
import time
import json
import os
import threading
import uuid
import sqlite3
from core.task_manager import task_manager
from epic_db import (
    clear_epic_games, upsert_epic_game, get_epic_auth,
    get_local_epic_ids, delete_epic_games_not_in, DB_PATH
)
from cache_manager import download_platform_image
from epic_client import fetch_epic_games, is_epic_authenticated, get_epic_account_name
from core.config import config
from core.steamgriddb import fetch_cover_from_steamgriddb
from core.cache import download_image_from_steamgriddb
import epic_login as epic_web_login  # 别名导入：避免与下方 epic_login() 路由函数重名

epic_bp = Blueprint('epic', __name__, url_prefix='/api/epic')

LEGENDARY_CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'legendary_config')
os.makedirs(LEGENDARY_CONFIG_DIR, exist_ok=True)


def _run_legendary_auth(exchange_code):
    """用一次性授权码完成 legendary 认证，返回 (成功与否, 错误信息)"""
    from epic_client import run_legendary
    result = run_legendary(["auth", "--token", exchange_code], LEGENDARY_CONFIG_DIR, timeout=60)
    if result is None or result.returncode != 0:
        err = result.stderr.strip() if result and result.stderr else 'legendary auth failed'
        return False, err
    return True, None

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
    if result is None or result.returncode != 0:
        return jsonify({"success": False, "error": result.stderr if result else "Auth failed"}), 400
    if is_epic_authenticated(LEGENDARY_CONFIG_DIR):
        return jsonify({"success": True, "account_name": get_epic_account_name(LEGENDARY_CONFIG_DIR)})
    else:
        return jsonify({"success": False, "error": "Authentication failed"}), 400

@epic_bp.route('/status')
def epic_status():
    if is_epic_authenticated(LEGENDARY_CONFIG_DIR):
        return jsonify({"authenticated": True, "account_name": get_epic_account_name(LEGENDARY_CONFIG_DIR)})
    return jsonify({"authenticated": False})


# ---------- 账密登录（邮箱 + 密码 + 两步验证，同 Heroic 体验） ----------

@epic_bp.route('/login_password', methods=['POST'])
def epic_login_password():
    data = request.json or {}
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    if not email or not password:
        return jsonify({"success": False, "error": "missing_credentials"}), 400

    result = epic_web_login.start_password_login(email, password)
    if result.get('mfa_required'):
        return jsonify(result)
    if not result.get('success'):
        return jsonify(result), 400

    ok, err = _run_legendary_auth(result['exchange_code'])
    if not ok:
        return jsonify({"success": False, "error": "legendary_failed", "detail": err}), 400
    return jsonify({"success": True,
                    "account_name": get_epic_account_name(LEGENDARY_CONFIG_DIR)})


@epic_bp.route('/login_mfa', methods=['POST'])
def epic_login_mfa():
    data = request.json or {}
    login_id = data.get('login_id') or ''
    code = (data.get('code') or '').strip()
    if not login_id or not code:
        return jsonify({"success": False, "error": "missing_credentials"}), 400

    result = epic_web_login.submit_mfa_code(login_id, code)
    if result.get('success'):
        ok, err = _run_legendary_auth(result['exchange_code'])
        if not ok:
            return jsonify({"success": False, "error": "legendary_failed", "detail": err}), 400
        return jsonify({"success": True,
                        "account_name": get_epic_account_name(LEGENDARY_CONFIG_DIR)})
    return jsonify(result), 400


@epic_bp.route('/login_cancel', methods=['POST'])
def epic_login_cancel():
    data = request.json or {}
    epic_web_login.cancel_login(data.get('login_id') or '')
    return jsonify({"success": True})


@epic_bp.route('/logout', methods=['POST'])
def epic_logout():
    from epic_client import run_legendary
    result = run_legendary(["auth", "--delete"], LEGENDARY_CONFIG_DIR, timeout=30)
    if result is None or result.returncode != 0:
        return jsonify({"success": False, "error": "logout_failed"}), 400
    return jsonify({"success": True})

@epic_bp.route('/sync', methods=['POST'])
def sync_epic_library():
    # 检查是否已登录
    if not is_epic_authenticated(LEGENDARY_CONFIG_DIR):
        return jsonify({"success": False, "error": "Not logged in"}), 401

    # 创建任务 ID
    task_id = str(uuid.uuid4())
    task_manager.create_task(task_id, 100)

    def run_sync():
        try:
            # 获取本地 ID
            local_ids = get_local_epic_ids()
            # 获取远程游戏
            remote_games = fetch_epic_games(None, LEGENDARY_CONFIG_DIR)
            if remote_games is None:
                task_manager.update_task(task_id, 100, '获取游戏列表失败')
                task_manager.finish_task(task_id, 'Failed to fetch games')
                return

            remote_ids = {game['game_id'] for game in remote_games}
            total = len(remote_ids)
            processed = 0
            task_manager.update_task(task_id, 10, f'开始同步，共 {total} 款游戏')

            # 先查找后插入，已存在则跳过
            for game in remote_games:
                app_name = game['game_id']
                if app_name in local_ids:
                    # 已存在，跳过
                    processed += 1
                    if processed % 10 == 0:
                        progress = 10 + int((processed / total) * 70)
                        task_manager.update_task(task_id, progress, f'已检查 {processed}/{total}')
                    continue

                # 新游戏，插入并下载图片（优先 SteamGridDB）
                title = game['name']
                cover_url = None
                try:
                    cover_url = fetch_cover_from_steamgriddb(title)
                except Exception as e:
                    print(f"SteamGridDB 获取失败 ({title}): {e}")
                if not cover_url:
                    # 回退到构造 CDN URL
                    cover_url = f"https://cdn2.epicgames.com/{app_name}/offer/{app_name}.jpg"
                if cover_url:
                    download_image_from_steamgriddb(cover_url, 'epic', app_name)
                upsert_epic_game(app_name, title, cover_url, app_name, int(time.time()))
                processed += 1
                if processed % 1 == 0:
                    progress = 10 + int((processed / total) * 70)
                    task_manager.update_task(task_id, progress, f'已处理 {processed}/{total}')

            # 删除多余游戏
            to_delete = local_ids - remote_ids
            if to_delete:
                delete_epic_games_not_in(remote_ids)
                task_manager.update_task(task_id, 90, f'删除本地多余游戏 ({len(to_delete)} 款)')

            task_manager.update_task(task_id, 100, f'同步完成 (共 {len(remote_games)} 款，删除 {len(to_delete)} 款)')
            task_manager.finish_task(task_id)
        except Exception as e:
            task_manager.update_task(task_id, 100, f'同步失败: {str(e)}')
            task_manager.finish_task(task_id, str(e))
            print(f"Epic 同步异常: {e}")
            import traceback
            traceback.print_exc()

    thread = threading.Thread(target=run_sync)
    thread.daemon = True
    thread.start()

    return jsonify({"task_id": task_id})