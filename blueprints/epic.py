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

epic_bp = Blueprint('epic', __name__, url_prefix='/api/epic')

LEGENDARY_CONFIG_DIR = os.path.join(os.path.dirname(__file__), '..', 'legendary_config')
os.makedirs(LEGENDARY_CONFIG_DIR, exist_ok=True)

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