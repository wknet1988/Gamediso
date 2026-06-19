from flask import Blueprint, request, jsonify
import time
import sqlite3
from gog_db import clear_gog_games, upsert_gog_game
from cache_manager import download_gog_image
from gog_client import get_gog_games, load_gog_token

gog_bp = Blueprint('gog', __name__, url_prefix='/api/gog')

@gog_bp.route('/sync', methods=['POST'])
def sync_gog_library():
    if not load_gog_token():
        return jsonify({"success": False, "error": "Not logged in"}), 401
    games = get_gog_games()
    if not games:
        return jsonify({"success": False, "error": "No games found"}), 404
    clear_gog_games()
    now = int(time.time())
    for game in games:
        game_id = game['game_id']
        title = game['title']
        image_url = game['image_url']
        if image_url:
            download_gog_image(image_url, game_id)
        upsert_gog_game(game_id, title, image_url, now)
    return jsonify({"success": True, "count": len(games)})

@gog_bp.route('/count')
def gog_count():
    from gog_db import count_gog_games
    count = count_gog_games()
    return jsonify({"count": count})

@gog_bp.route('/status')
def gog_status():
    if load_gog_token():
        return jsonify({"authenticated": True, "account_name": "GOG User"})
    return jsonify({"authenticated": False})

# 如果使用油猴脚本同步，保留此接口
@gog_bp.route('/sync_from_extension', methods=['POST'])
def gog_sync_from_extension():
    data = request.json
    games = data.get('games', [])
    if not games:
        return jsonify({"success": False, "error": "No games data"}), 400
    clear_gog_games()
    now = int(time.time())
    for game in games:
        game_id = str(game.get('game_id'))
        title = game.get('title', 'Unknown')
        image_url = game.get('image_url', '')
        if image_url:
            download_gog_image(image_url, game_id)
        upsert_gog_game(game_id, title, image_url, now)
    return jsonify({"success": True, "count": len(games)})