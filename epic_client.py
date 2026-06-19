import subprocess
import json
import os
import sys
import shutil
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def find_legendary():
    legendary = shutil.which('legendary')
    if legendary:
        return legendary
    scripts_dir = os.path.join(sys.prefix, 'Scripts')
    legendary_exe = os.path.join(scripts_dir, 'legendary.exe')
    if os.path.exists(legendary_exe):
        return legendary_exe
    raise FileNotFoundError("legendary not found")

def run_legendary(args, config_dir=None):
    legendary_exe = find_legendary()
    env = os.environ.copy()
    if config_dir:
        env['LEGENDARY_CONFIG_PATH'] = config_dir
    return subprocess.run(
        [legendary_exe] + args,
        capture_output=True,
        text=True,
        env=env,
        timeout=60
    )

def is_epic_authenticated(config_dir=None):
    if not config_dir:
        config_dir = os.path.expanduser("~/.config/legendary")
    result = run_legendary(["list-games", "--json", "--limit=1"], config_dir)
    return result.returncode == 0

def get_epic_account_name(config_dir=None):
    if not config_dir:
        config_dir = os.path.expanduser("~/.config/legendary")
    user_json = os.path.join(config_dir, 'user.json')
    if os.path.exists(user_json):
        with open(user_json, 'r') as f:
            data = json.load(f)
            return data.get('displayName', 'Epic User')
    return None

def fetch_epic_game_details(app_name: str, config_dir: str) -> dict:
    result = run_legendary(["info", app_name, "--json"], config_dir)
    if result.returncode != 0:
        return {}
    try:
        data = json.loads(result.stdout)
        asset_info = data.get('asset_info', {})
        key_images = asset_info.get('key_images', [])
        for img in key_images:
            if img.get('type') in ('OfferImageTall', 'Thumbnail'):
                return {'cover_url': img.get('url', '')}
        assets = asset_info.get('assets', [])
        for asset in assets:
            if asset.get('type') == 'THUMBNAIL':
                return {'cover_url': asset.get('url', '')}
    except Exception as e:
        print(f"解析 Epic 游戏详情失败: {app_name}, {e}")
    return {}

def fetch_epic_games(access_token=None, config_dir=None):
    if not config_dir:
        config_dir = os.path.expanduser("~/.config/legendary")
    result = run_legendary(["list-games", "--json"], config_dir)
    if result.returncode != 0:
        return []
    games = json.loads(result.stdout)
    game_list = []
    for game in games:
        app_name = game.get('app_name')
        title = game.get('app_title')
        details = fetch_epic_game_details(app_name, config_dir)
        cover_url = details.get('cover_url', '')
        if not cover_url:
            cover_url = f"https://cdn2.epicgames.com/{app_name}/offer/{app_name}.jpg"
        game_list.append({
            'game_id': app_name,
            'name': title,
            'header_url': cover_url,
            'sandbox': app_name,
        })
    return game_list