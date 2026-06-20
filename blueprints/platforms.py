from flask import Blueprint, jsonify
import os
from core.config import config
from epic_db import count_epic_games
from gog_db import count_gog_games
from cubejoy_db import count_cubejoy_games

platform_bp = Blueprint('platform', __name__, url_prefix='/api/platforms')

@platform_bp.route('')
def get_platforms():
    platforms = []

    if config.get('steamid') and config.get('api_key'):
        platforms.append({"id": "steam", "name": "Steam", "icon": "🎮"})

    epic_credential_file = os.path.join(os.path.dirname(__file__), '..', 'legendary_config', 'user.json')
    if os.path.exists(epic_credential_file) or (config.get('epic_client_id') and config.get('epic_client_secret')):
        platforms.append({"id": "epic", "name": "Epic Games", "icon": "✨"})

    try:
        if count_gog_games() > 0:
            platforms.append({"id": "gog", "name": "GOG", "icon": "📀"})
    except:
        pass

    try:
        if count_cubejoy_games() > 0:
            platforms.append({"id": "cubejoy", "name": "Cubejoy", "icon": "🧊"})
    except:
        pass

    return jsonify(platforms)