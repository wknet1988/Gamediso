from flask import Blueprint, send_file, abort
import sqlite3
import os
from core.cache import get_platform_image_path, download_platform_image

images_bp = Blueprint('images', __name__, url_prefix='/images')

def send_cached_file(file_path):
    """发送文件并设置强缓存头"""
    response = send_file(file_path, conditional=True)
    response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
    return response

def get_placeholder_path(platform: str) -> str:
    filename = {
        'steam': 'steam_placeholder.png',
        'epic': 'epic_placeholder.png',
        'gog': 'gog_placeholder.png',
        'cubejoy': 'cubejoy_placeholder.png',
    }.get(platform, 'default_placeholder.png')
    return os.path.join(os.path.dirname(__file__), '..', 'static', filename)

@images_bp.route('/<int:appid>.jpg')
def steam_image(appid):
    local_path = get_platform_image_path('steam', str(appid))
    if not local_path.exists():
        conn = sqlite3.connect('steam_games.db')
        c = conn.cursor()
        c.execute("SELECT header_url FROM games WHERE appid = ?", (appid,))
        row = c.fetchone()
        conn.close()
        if row:
            download_platform_image(row[0], 'steam', str(appid))
    if local_path.exists():
        return send_cached_file(local_path)
    else:
        placeholder = get_placeholder_path('steam')
        if os.path.exists(placeholder):
            return send_file(placeholder, mimetype='image/png')
        else:
            abort(404)

@images_bp.route('/epic/<game_id>.jpg')
def epic_image(game_id):
    local_path = get_platform_image_path('epic', game_id)
    if not local_path.exists():
        conn = sqlite3.connect('epic_games.db')
        c = conn.cursor()
        c.execute("SELECT header_url FROM epic_games WHERE game_id = ?", (game_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            # 尝试下载图片
            download_platform_image(row[0], 'epic', game_id)
    if local_path.exists():
        return send_file(local_path, conditional=True, max_age=31536000, immutable=True)
    else:
        placeholder = get_placeholder_path('epic')
        if os.path.exists(placeholder):
            return send_file(placeholder, mimetype='image/png')
        else:
            abort(404)

@images_bp.route('/gog/<game_id>.jpg')
def gog_image(game_id):
    local_path = get_platform_image_path('gog', game_id)
    if not local_path.exists():
        conn = sqlite3.connect('gog_games.db')
        c = conn.cursor()
        c.execute("SELECT image_url FROM gog_games WHERE game_id = ?", (game_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            download_platform_image(row[0], 'gog', game_id)
    if local_path.exists():
        return send_file(local_path, conditional=True, max_age=31536000, immutable=True)
    else:
        placeholder = get_placeholder_path('gog')
        if os.path.exists(placeholder):
            return send_file(placeholder, mimetype='image/png')
        else:
            abort(404)

@images_bp.route('/cubejoy/<game_id>.jpg')
def cubejoy_image(game_id):
    local_path = get_platform_image_path('cubejoy', game_id)
    if not local_path.exists():
        conn = sqlite3.connect('cubejoy_games.db')
        c = conn.cursor()
        c.execute("SELECT image_url FROM cubejoy_games WHERE game_id = ?", (game_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            url = row[0]
            if url.startswith('//'):
                url = 'https:' + url
            download_platform_image(url, 'cubejoy', game_id)
    if local_path.exists():
        return send_cached_file(local_path)
    else:
        placeholder = get_placeholder_path('cubejoy')
        if os.path.exists(placeholder):
            return send_file(placeholder, mimetype='image/png')
        else:
            abort(404)