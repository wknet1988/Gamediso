import requests
import json
from core.config import config

def get_steamgriddb_api_key():
    return config.get('steamgriddb_api_key', '')

def search_game(game_name: str) -> str:
    """通过游戏名称搜索，返回第一个匹配的 game_id"""
    api_key = get_steamgriddb_api_key()
    if not api_key:
        return None
    url = f"https://www.steamgriddb.com/api/v2/search/autocomplete/{game_name}"
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('data') and len(data['data']) > 0:
                return str(data['data'][0]['id'])
    except Exception as e:
        print(f"SteamGridDB 搜索失败: {game_name}, {e}")
    return None

def get_grid_image_url(game_id: str) -> str:
    """获取游戏的第一张 grid 图片 URL（600x900）"""
    api_key = get_steamgriddb_api_key()
    if not api_key:
        return None
    url = f"https://www.steamgriddb.com/api/v2/grids/game/{game_id}?dimensions=600x900"
    headers = {'Authorization': f'Bearer {api_key}'}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('data') and len(data['data']) > 0:
                return data['data'][0]['url']
    except Exception as e:
        print(f"SteamGridDB 获取图片失败: {game_id}, {e}")
    return None

def fetch_cover_from_steamgriddb(game_name: str) -> str:
    """综合函数：通过游戏名称获取封面图 URL"""
    game_id = search_game(game_name)
    if game_id:
        return get_grid_image_url(game_id)
    return None