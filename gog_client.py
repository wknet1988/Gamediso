import subprocess
import json
import os
import sys
import shutil
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def find_gogdl():
    gogdl = shutil.which('gogdl')
    if gogdl:
        return gogdl
    scripts_dir = os.path.join(sys.prefix, 'Scripts')
    gogdl_exe = os.path.join(scripts_dir, 'gogdl.exe')
    if os.path.exists(gogdl_exe):
        return gogdl_exe
    raise FileNotFoundError("gogdl not found")

def run_gogdl(args):
    gogdl_path = find_gogdl()
    return subprocess.run(
        [gogdl_path] + args,
        capture_output=True,
        text=True,
        timeout=60
    )

def fetch_gog_game_details(game_id: str) -> dict:
    api_url = f"https://api.gog.com/products/{game_id}?locale=en-US&expand=images"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(api_url, timeout=10, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            images = data.get('images', {})
            for key in ['cover', 'background', 'logo']:
                if images.get(key):
                    return {'cover_url': images[key]}
    except Exception as e:
        print(f"GOG API 异常: {e}")
    return {}

def get_gog_games():
    result = run_gogdl(["owned", "--json"])
    if result.returncode != 0:
        return []
    games = json.loads(result.stdout)
    game_list = []
    for game in games:
        game_id = str(game.get('id'))
        title = game.get('title', 'Unknown')
        details = fetch_gog_game_details(game_id)
        cover_url = details.get('cover_url', '')
        if not cover_url:
            cover_url = game.get('image', '')
        game_list.append({
            'game_id': game_id,
            'title': title,
            'image_url': cover_url,
        })
    return game_list

def load_gog_token():
    # 简化：检查 gogdl 是否已认证（通过检测配置文件）
    # 实际项目中可做更完善的检查
    return True