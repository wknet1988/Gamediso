from flask import Blueprint, request, jsonify
from database import get_all_games, get_shelves
from epic_db import get_all_epic_games
from gog_db import get_all_gog_games
from cubejoy_db import get_all_cubejoy_games

games_bp = Blueprint('games', __name__, url_prefix='/api/games')

@games_bp.route('')
def api_games():
    platform = request.args.get('platform', 'steam')
    limit = int(request.args.get('limit', 28))
    offset = int(request.args.get('offset', 0))
    search = request.args.get('search', '').strip()

    if platform == 'steam':
        games_raw = get_all_games()
        games = [
            {
                "id": g["appid"],
                "name": g["name"],
                "image_url": f"/images/steam/{g['appid']}.jpg",
                "original_url": g.get("header_url", g.get("image_url", "")),
                "type": g.get("type", "owned")
            }
            for g in games_raw
        ]
    elif platform == 'epic':
        games_raw = get_all_epic_games()
        games = [
            {
                "id": g["game_id"],
                "name": g["name"],
                "image_url": f"/images/epic/{g['game_id']}.jpg",
                "original_url": g.get("header_url", ""),
            }
            for g in games_raw
        ]
    elif platform == 'gog':
        games_raw = get_all_gog_games()
        games = [
            {
                "id": g["game_id"],
                "name": g["name"],
                "image_url": f"/images/gog/{g['game_id']}.jpg",
                "original_url": g.get("image_url", ""),
            }
            for g in games_raw
        ]
    elif platform == 'cubejoy':
        games_raw = get_all_cubejoy_games()
        games = [
            {
                "id": g["game_id"],
                "s_id": g.get("s_id", ""),
                "name": g["name"],
                "image_url": f"/images/cubejoy/{g['game_id']}.jpg",
                "original_url": g.get("image_url", ""),
            }
            for g in games_raw
        ]
    else:
        return jsonify({"error": "Unsupported platform"}), 400

    if search:
        games = [g for g in games if search.lower() in g['name'].lower()]

    total = len(games)
    paged = games[offset:offset+limit]
    return jsonify({"games": paged, "total": total})

@games_bp.route('/shelves')
def api_get_shelves():
    shelves = get_shelves()
    return jsonify(shelves)