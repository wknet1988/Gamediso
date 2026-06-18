import requests
import urllib3
import os
import json
import time
from urllib.parse import urlencode

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# GOG OAuth 配置（使用 GOG Galaxy 公开的 client_id 和 secret）
GOG_CLIENT_ID = "46899977096215655"
GOG_CLIENT_SECRET = "9d85c43b785249a9a123eafc4d5d2c3a"  # 公开的 secret
GOG_AUTH_URL = "https://auth.gog.com/auth"
GOG_TOKEN_URL = "https://auth.gog.com/token"
GOG_API_URL = "https://api.gog.com"

# 配置存储目录
GOG_CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'gog_config')
os.makedirs(GOG_CONFIG_DIR, exist_ok=True)

def get_gog_auth_url(redirect_uri):
    """生成 GOG 授权 URL"""
    params = {
        'client_id': GOG_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'layout': 'client2'
    }
    return f"{GOG_AUTH_URL}?{urlencode(params)}"

def exchange_code_for_token(code, redirect_uri):
    """用授权码换取 access_token 和 refresh_token"""
    data = {
        'client_id': GOG_CLIENT_ID,
        'client_secret': GOG_CLIENT_SECRET,
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
    }
    resp = requests.post(GOG_TOKEN_URL, data=data, verify=False)
    if resp.status_code == 200:
        token_data = resp.json()
        # 保存 token 到文件
        with open(os.path.join(GOG_CONFIG_DIR, 'token.json'), 'w') as f:
            json.dump(token_data, f)
        return token_data
    return None

def load_gog_token():
    token_path = os.path.join(GOG_CONFIG_DIR, 'token.json')
    if os.path.exists(token_path):
        with open(token_path, 'r') as f:
            return json.load(f)
    return None

def refresh_gog_token():
    token = load_gog_token()
    if not token or 'refresh_token' not in token:
        return False
    data = {
        'client_id': GOG_CLIENT_ID,
        'client_secret': GOG_CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': token['refresh_token'],
    }
    resp = requests.post(GOG_TOKEN_URL, data=data, verify=False)
    if resp.status_code == 200:
        new_token = resp.json()
        with open(os.path.join(GOG_CONFIG_DIR, 'token.json'), 'w') as f:
            json.dump(new_token, f)
        return True
    return False

def get_gog_account_name():
    token = load_gog_token()
    if not token:
        return None
    headers = {'Authorization': f'Bearer {token["access_token"]}'}
    resp = requests.get(f"{GOG_API_URL}/account/me", headers=headers, verify=False)
    if resp.status_code == 200:
        data = resp.json()
        return data.get('username') or data.get('email')
    return None

def get_gog_games():
    token = load_gog_token()
    if not token:
        return []
    # 检查 token 是否过期（简单判断，实际可存储过期时间）
    if token.get('expires_in'):
        # 如果过期，尝试刷新
        refresh_gog_token()
        token = load_gog_token()
    headers = {'Authorization': f'Bearer {token["access_token"]}'}
    resp = requests.get(f"{GOG_API_URL}/user/games", headers=headers, verify=False)
    if resp.status_code != 200:
        return []
    data = resp.json()
    games = data.get('games', [])
    result = []
    for game in games:
        game_id = str(game.get('id'))
        title = game.get('title', 'Unknown')
        image_url = game.get('image')
        if not image_url:
            image_url = f"https://images.gog.com/{game_id}.jpg"
        result.append({
            'game_id': game_id,
            'title': title,
            'image_url': image_url
        })
    return result