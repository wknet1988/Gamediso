import os
import json
import time
import webbrowser
from threading import Timer
from flask import Flask, request, jsonify, session, redirect, render_template, send_file
from flask_cors import CORS
import requests
import urllib3
import subprocess
import json
import os
import time
import sys
import shutil
import tempfile

# 禁用 SSL 警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 导入自定义模块
from database import *
from steam_client import *
from cache_manager import *
from epic_client import get_epic_auth_url, exchange_code_for_token, refresh_access_token, fetch_epic_games
from epic_db import init_epic_db, get_all_epic_games, upsert_epic_game, clear_epic_games, save_epic_auth, get_epic_auth
from cache_manager import get_platform_image_path, download_platform_image

# 导入 gog_client 相关函数
from gog_client import (get_gog_auth_url, exchange_code_for_token, 
                        load_gog_token, get_gog_account_name, get_gog_games)
from gog_db import init_gog_db, get_all_gog_games, upsert_gog_game, clear_gog_games
from cache_manager import get_gog_image_path, download_gog_image

from cubejoy_db import init_cubejoy_db, get_all_cubejoy_games, upsert_cubejoy_game, clear_cubejoy_games, count_cubejoy_games
from cache_manager import get_cubejoy_image_path, download_cubejoy_image

app = Flask(__name__)
app.secret_key = 'steam_shelf_secret_key_change_me'
CORS(app)

CONFIG_FILE = "config.json"

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {"steamid": None, "api_key": None, "steam_path": None, "epic_client_id": "", "epic_client_secret": ""}
    try:
        with open(CONFIG_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return {"steamid": None, "api_key": None, "steam_path": None, "epic_client_id": "", "epic_client_secret": ""}
            return json.loads(content)
    except:
        return {"steamid": None, "api_key": None, "steam_path": None, "epic_client_id": "", "epic_client_secret": ""}

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

config = load_config()

# 确保 config 中包含 Epic 相关字段
if 'epic_client_id' not in config:
    config['epic_client_id'] = ''
if 'epic_client_secret' not in config:
    config['epic_client_secret'] = ''
save_config(config)

# 初始化 Steam 数据库
init_db()

# 初始化 Epic 数据库
init_epic_db()

# 在 main 函数中，初始化完其他数据库后
init_gog_db()

init_cubejoy_db()

# ==================== Steam 相关函数 ====================
def refresh_games_library(force=False):
    steamid = session.get('steamid')
    api_key = session.get('api_key')
    if not steamid or not api_key:
        return False
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT MAX(last_updated) FROM games")
    row = c.fetchone()
    last = row[0] if row[0] else 0
    conn.close()
    
    now = int(time.time())
    if not force and (now - last) < 86400:
        return True
    
    try:
        # 1. 获取家庭组信息（使用 api_key）
        family_info = get_family_group_for_user(api_key, steamid)
        if family_info:
            family_games = fetch_family_shared_games(api_key, family_info['family_groupid'])
        else:
            family_games = []
        
        # 2. 获取自己拥有的游戏
        owned_games = fetch_owned_games(api_key, steamid)
        
        # 3. 合并去重
        all_games = owned_games.copy()
        owned_appids = {g['appid'] for g in owned_games}
        for game in family_games:
            if game['appid'] not in owned_appids:
                all_games.append(game)
        
        # 4. 更新数据库和图片缓存
        # 在 refresh_games_library 中
        for game in owned_games:
            upsert_game(game['appid'], game['name'], game['header_url'], now, 'owned')
        for game in family_games:
            if game['appid'] not in owned_appids:
                upsert_game(game['appid'], game['name'], game['header_url'], now, 'shared')
        
        # 5. 更新家庭组的自定义列表（如果用户提供了 Steam 路径）
        steam_path = session.get('steam_path') or config.get('steam_path')
        if steam_path:
            refresh_shelves_from_steam()
        
        return True
    except Exception as e:
        print(f"刷新游戏库失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def refresh_shelves_from_steam():
    steam_path = session.get('steam_path') or config.get('steam_path')
    steamid = session.get('steamid')
    if not steam_path or not steamid:
        return False
    groups = parse_steam_groups(steam_path, steamid)
    if not groups:
        return False
    clear_shelves()
    for group_name, appids in groups.items():
        shelf_type = 'favorite' if group_name == '我的最爱' else 'custom'
        shelf_id = add_shelf(group_name, shelf_type)
        for idx, appid in enumerate(appids):
            add_game_to_shelf(shelf_id, appid, idx)
    return True

# ==================== Epic 相关函数 ====================
def sync_epic_library_task():
    try:
        access_token = get_epic_auth('access_token')
        if not access_token:
            return
        games = fetch_epic_games(access_token)
        now = int(time.time())
        clear_epic_games()
        for game in games:
            upsert_epic_game(game['game_id'], game['name'], game['header_url'], game['sandbox'], now)
            if game['header_url']:
                download_platform_image(game['header_url'], 'epic', game['game_id'])
    except Exception as e:
        print(f"Epic 同步失败: {e}")

def find_legendary():
    """查找 legendary 可执行文件"""
    # 优先使用环境变量中的 legendary
    legendary = shutil.which('legendary')
    if legendary:
        return legendary
    # 在 Python Scripts 目录下查找
    scripts_dir = os.path.join(sys.prefix, 'Scripts')
    legendary_exe = os.path.join(scripts_dir, 'legendary.exe')
    if os.path.exists(legendary_exe):
        return legendary_exe
    raise FileNotFoundError("legendary not found. Please install legendary-gl: pip install legendary-gl")

def run_legendary(args):
    """运行 legendary 命令，返回 subprocess.CompletedProcess"""
    legendary_exe = find_legendary()
    env = os.environ.copy()
    env['LEGENDARY_CONFIG_PATH'] = LEGENDARY_CONFIG_DIR
    return subprocess.run(
        [legendary_exe] + args,
        capture_output=True,
        text=True,
        env=env,
        timeout=60
    )

def is_epic_authenticated():
    """检查是否已登录"""
    result = run_legendary(["list-games", "--json", "--limit=1"])
    return result.returncode == 0

def get_epic_account_name():
    """从 user.json 获取账号名"""
    user_json = os.path.join(LEGENDARY_CONFIG_DIR, 'user.json')
    if os.path.exists(user_json):
        with open(user_json, 'r') as f:
            data = json.load(f)
            return data.get('displayName', 'Epic User')
    return None

# ==================== 路由定义 ====================
@app.route('/')
def index():
    return render_template('index.html')

# Steam 图片代理
@app.route('/images/<int:appid>.jpg')
def get_image(appid):
    local_path = get_cached_image_path(appid)
    if local_path.exists() and not is_image_valid(local_path):
        # 删除损坏的文件
        local_path.unlink()
    if not local_path.exists():
        # 从数据库获取原始 URL 并下载
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT header_url FROM games WHERE appid = ?", (appid,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            download_image(row[0], appid)
    if local_path.exists() and is_image_valid(local_path):
        return send_file(local_path, mimetype='image/jpeg')
    else:
        return "", 404

# Epic 图片代理
@app.route('/images_epic/<game_id>.jpg')
def epic_image(game_id):
    local_path = get_platform_image_path('epic', game_id)
    if local_path.exists() and not is_image_valid(local_path):
        # 删除损坏的文件
        local_path.unlink()
    if not local_path.exists():
        # 尝试从数据库获取 URL 并下载
        conn = sqlite3.connect("epic_games.db")
        c = conn.cursor()
        c.execute("SELECT header_url FROM epic_games WHERE game_id = ?", (game_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            download_platform_image(row[0], 'epic', game_id)
    if local_path.exists():
        return send_file(local_path, mimetype='image/jpeg')
    else:
        # 返回默认占位图
        placeholder = os.path.join(app.static_folder, 'epic_placeholder.png')
        if os.path.exists(placeholder):
            return send_file(placeholder, mimetype='image/png')
        else:
            # 最后返回一个透明的 1x1 像素 PNG
            return "", 204

# ==================== Steam 认证和配置 ====================
@app.route('/api/status')
def api_status():
    if not session.get('steamid') and config.get('steamid'):
        session['steamid'] = config['steamid']
    if not session.get('api_key') and config.get('api_key'):
        session['api_key'] = config['api_key']
    if not session.get('steam_path') and config.get('steam_path'):
        session['steam_path'] = config['steam_path']
    
    steamid = session.get('steamid')
    api_key = session.get('api_key')
    steam_path = session.get('steam_path')
    if steamid and api_key and steam_path:
        return jsonify({"logged_in": True, "steamid": steamid, "has_steam_path": True})
    elif steamid and api_key:
        return jsonify({"logged_in": False, "steamid": steamid, "need_steam_path": True})
    elif steamid:
        return jsonify({"logged_in": False, "steamid": steamid, "need_api_key": True})
    else:
        return jsonify({"logged_in": False})

@app.route('/api/login')
def api_login():
    return_to = request.url_root.rstrip('/') + '/api/auth'
    login_url = get_steam_login_url(return_to)
    return jsonify({"login_url": login_url})

@app.route('/api/auth')
def api_auth():
    callback_url = request.url
    steamid = validate_steam_callback(callback_url)
    if steamid:
        session['steamid'] = steamid
        config['steamid'] = steamid
        save_config(config)
        return redirect('/')
    else:
        return "登录失败", 400

@app.route('/api/set_api_key', methods=['POST'])
def api_set_api_key():
    data = request.json
    api_key = data.get('api_key')
    if api_key:
        session['api_key'] = api_key
        config['api_key'] = api_key
        save_config(config)
        refresh_games_library(force=True)
        return jsonify({"success": True})
    return jsonify({"success": False}), 400

@app.route('/api/set_steam_path', methods=['POST'])
def api_set_steam_path():
    data = request.json
    steam_path = data.get('steam_path')
    if steam_path and os.path.exists(steam_path):
        session['steam_path'] = steam_path
        config['steam_path'] = steam_path
        save_config(config)
        refresh_shelves_from_steam()
        return jsonify({"success": True})
    return jsonify({"success": False, "error": "路径无效"}), 400

@app.route('/api/init_library', methods=['POST'])
def api_init_library():
    success = refresh_games_library(force=True)
    if success:
        return jsonify({"success": True})
    else:
        return jsonify({"success": False}), 500

# 旧版 shelves 接口（保留兼容）
@app.route('/api/shelves', methods=['GET'])
def api_get_shelves():
    shelves = get_shelves()
    return jsonify(shelves)

# ==================== 家庭库同步（使用 access_token） ====================
def get_family_info_with_token(access_token, steamid):
    url = 'https://api.steampowered.com/IFamilyGroupsService/GetFamilyGroupForUser/v1/'
    params = {
        'access_token': access_token,
        'steamid': steamid,
        'include_family_group_response': True,
    }
    resp = requests.get(url, params=params, verify=False)
    if resp.status_code != 200:
        return None
    data = resp.json()
    response = data.get('response', {})
    if 'family_groupid' not in response:
        return None
    family_group = response.get('family_group', {})
    members = family_group.get('members', [])
    # 获取成员昵称
    steamid_to_name = {}
    if members:
        name_url = 'https://api.steampowered.com/IPlayerService/GetPlayerLinkDetails/v1/'
        name_params = {'access_token': access_token}
        for idx, m in enumerate(members):
            name_params[f'steamids[{idx}]'] = m['steamid']
        name_resp = requests.get(name_url, params=name_params, verify=False)
        if name_resp.status_code == 200:
            name_data = name_resp.json()
            accounts = name_data.get('response', {}).get('accounts', [])
            for acc in accounts:
                steamid_to_name[acc['public_data']['steamid']] = acc['public_data']['persona_name']
    for m in members:
        m['userName'] = steamid_to_name.get(m['steamid'], 'Unknown')
    return {
        'family_groupid': response['family_groupid'],
        'family_name': family_group.get('name', ''),
        'family_member': members,
        'steamIdtoName': steamid_to_name
    }

def get_family_shared_games_with_token(access_token, family_groupid):
    url = 'https://api.steampowered.com/IFamilyGroupsService/GetSharedLibraryApps/v1/'
    params = {
        'access_token': access_token,
        'family_groupid': family_groupid,
        'include_own': True,
        'include_excluded': False,
        'include_non_games': False,
    }
    resp = requests.get(url, params=params, verify=False)
    if resp.status_code != 200:
        return []
    data = resp.json()
    apps = data.get('response', {}).get('apps', [])
    result = []
    for app in apps:
        if app.get('exclude_reason', 0) == 0:
            result.append({
                'appid': app['appid'],
                'name': app.get('name', 'Unknown'),
                'header_url': f'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{app["appid"]}/header.jpg',
                'owners': app.get('owner_steamids', []),
                'rt_time_acquired': app.get('rt_time_acquired', 0)
            })
    return result

@app.route('/api/sync_family_library', methods=['POST'])
def api_sync_family_library():
    data = request.json
    access_token = data.get('access_token')
    steamid = data.get('steamid')
    if not access_token or not steamid:
        return jsonify({"success": False, "error": "Missing access_token or steamid"}), 400
    
    family_info = get_family_info_with_token(access_token, steamid)
    if not family_info:
        return jsonify({"success": False, "error": "Cannot get family info. Make sure you are in a Steam Family."}), 400
    
    family_games = get_family_shared_games_with_token(access_token, family_info['family_groupid'])
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    now = int(time.time())
    
    # 获取所有自己购买的游戏 ID (type='owned')
    c.execute("SELECT appid FROM games WHERE type = 'owned'")
    owned_appids = {row[0] for row in c.fetchall()}
    
    for game in family_games:
        appid = game['appid']
        name = game['name']
        header_url = game['header_url']
        
        # 如果游戏已经被标记为 owned，则跳过（不改为 shared）
        if appid in owned_appids:
            continue
        
        # 检查是否已存在（可能是之前同步的 shared）
        c.execute("SELECT 1 FROM games WHERE appid = ?", (appid,))
        exists = c.fetchone() is not None
        if exists:
            c.execute("UPDATE games SET name = ?, header_url = ?, last_updated = ? WHERE appid = ?",
                      (name, header_url, now, appid))
        else:
            c.execute("INSERT INTO games (appid, name, header_url, last_updated, type) VALUES (?, ?, ?, ?, ?)",
                      (appid, name, header_url, now, 'shared'))
        
        if not get_cached_image_path(appid).exists():
            download_image(header_url, appid)
    
    conn.commit()
    conn.close()
    
    return jsonify({"success": True, "family_name": family_info['family_name'], "games_count": len(family_games)})


@app.route('/api/family/count')
def family_count():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM games WHERE type = 'shared'")
    count = c.fetchone()[0]
    conn.close()
    return jsonify({"count": count})

# ==================== Epic 相关路由 ====================
epic_client_id = config.get('epic_client_id')
epic_client_secret = config.get('epic_client_secret')
epic_redirect_uri = "http://localhost:5000/api/epic/callback"

@app.route('/api/epic/login')
def epic_login():
    # Legendary 的授权 URL，用于触发登录
    return jsonify({"login_url": "https://legendary.gl/epiclogin"})

@app.route('/api/epic/callback')
def epic_callback():
    code = request.args.get('code')
    if not code:
        return "Missing code", 400

    # 调用 Legendary 命令行交换授权码
    cmd = ["legendary", "auth", "--code", code]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        # 读取认证后的用户信息
        with open(os.path.join(EPIC_AUTH_DIR, "user.json"), "r") as f:
            user_data = json.load(f)
        return redirect('/')
    except subprocess.CalledProcessError as e:
        return f"Authentication failed: {e.stderr}", 400

# Legendary 配置目录
LEGENDARY_CONFIG_DIR = os.path.join(os.path.dirname(__file__), 'legendary_config')
os.makedirs(LEGENDARY_CONFIG_DIR, exist_ok=True)

@app.route('/api/epic/status')
def epic_status():
    if is_epic_authenticated():
        return jsonify({"authenticated": True, "account_name": get_epic_account_name()})
    return jsonify({"authenticated": False})

@app.route('/api/epic/auth_code', methods=['POST'])
def epic_auth_code():
    data = request.json
    code = data.get('code')
    if not code:
        return jsonify({"success": False, "error": "Missing code"}), 400
    try:
        result = run_legendary(["auth", "--code", code])
        if result.returncode != 0:
            return jsonify({"success": False, "error": result.stderr}), 400
        if is_epic_authenticated():
            return jsonify({"success": True, "account_name": get_epic_account_name()})
        else:
            return jsonify({"success": False, "error": "Authentication failed"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/epic/sync', methods=['POST'])
def sync_epic_library():
    if not is_epic_authenticated():
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    result = run_legendary(["list-games", "--json"])
    if result.returncode != 0:
        return jsonify({"success": False, "error": result.stderr}), 500
    
    games = json.loads(result.stdout)
    from epic_db import clear_epic_games, upsert_epic_game
    from cache_manager import download_platform_image
    
    clear_epic_games()
    now = int(time.time())
    for game in games:
        app_name = game['app_name']
        title = game['app_title']
        # 使用 Epic 官方 CDN 图片 URL（兼容旧游戏）
        cover_url = f"https://cdn2.epicgames.com/{app_name}/offer/{app_name}.jpg"
        # 尝试下载图片（如果失败，前端会显示占位图）
        download_platform_image(cover_url, 'epic', app_name)
        upsert_epic_game(app_name, title, cover_url, app_name, now)
    
    return jsonify({"success": True, "count": len(games)})


@app.route('/api/epic/games')
def api_epic_games():
    limit = int(request.args.get('limit', 28))
    offset = int(request.args.get('offset', 0))
    search = request.args.get('search', '').strip()
    
    from epic_db import get_all_epic_games
    all_games = get_all_epic_games()
    
    if search:
        all_games = [g for g in all_games if search.lower() in g['name'].lower()]
    
    total = len(all_games)
    paged = all_games[offset:offset+limit]
    
    # 为每个游戏添加图片 URL
    for g in paged:
        g['image_url'] = f"/images_epic/{g['game_id']}.jpg"
        # 确保返回字段统一为 id, name, image_url
        g['id'] = g.pop('game_id')
    
    return jsonify({"games": paged, "total": total})

# ==================== 统一游戏接口（支持 platform 参数） ====================
@app.route('/api/games')
def api_games():
    platform = request.args.get('platform', 'steam')
    limit = int(request.args.get('limit', 28))
    offset = int(request.args.get('offset', 0))
    search = request.args.get('search', '').strip()
    
    if platform == 'steam':
        games_raw = get_all_games()
        games = [{"id": g["appid"], "name": g["name"], "image_url": f"/images/{g['appid']}.jpg", "type": g.get("type", "owned")} for g in games_raw]
    elif platform == 'epic':
        games_raw = get_all_epic_games()
        games = [{"id": g["game_id"], "name": g["name"], "image_url": f"/images_epic/{g['game_id']}.jpg"} for g in games_raw]
    elif platform == 'gog':
        games_raw = get_all_gog_games()
        games = [{"id": g["game_id"], "name": g["name"], "image_url": f"/images_gog/{g['game_id']}.jpg"} for g in games_raw]
    elif platform == 'cubejoy':
        games_raw = get_all_cubejoy_games()
        games = [{"id": g["game_id"], "s_id": g["s_id"], "name": g["name"], "image_url": f"/images_cubejoy/{g['game_id']}.jpg"} for g in games_raw]
    else:
        return jsonify({"error": "Unsupported platform"}), 400
    
    if search:
        games = [g for g in games if search.lower() in g['name'].lower()]
    total = len(games)
    paged = games[offset:offset+limit]
    return jsonify({"games": paged, "total": total})

# ==================== 平台列表接口 ====================

@app.route('/api/platforms')
def get_platforms():
    platforms = []
    # Steam
    if config.get('steamid') and config.get('api_key'):
        platforms.append({"id": "steam", "name": "Steam", "icon": "🎮"})
    # Epic
    epic_credential_file = os.path.join(LEGENDARY_CONFIG_DIR, 'user.json')
    if os.path.exists(epic_credential_file) or (config.get('epic_client_id') and config.get('epic_client_secret')):
        platforms.append({"id": "epic", "name": "Epic Games", "icon": "✨"})
    # GOG: 只有数据库中有游戏时才显示
    from gog_db import count_gog_games
    if count_gog_games() > 0:
        platforms.append({"id": "gog", "name": "GOG", "icon": "📀"})
    # Cubejoy: 只有数据库中有游戏时才显示
    if count_cubejoy_games() > 0:
        platforms.append({"id": "cubejoy", "name": "Cubejoy 方块", "icon": "🧊"})
    return jsonify(platforms)

# ==================== 静态文件路由（油猴脚本下载） ====================
@app.route('/static/family_sync.user.js')
def download_script():
    response = send_file('static/family_sync.user.js', mimetype='application/javascript; charset=utf-8')
    response.headers['Content-Disposition'] = 'attachment; filename=family_sync.user.js'
    return response

# ==================== GOG 相关路由 ====================

# 配置 GOG 回调地址
GOG_REDIRECT_URI = "http://localhost:5000/api/gog/callback"

from flask import redirect

@app.route('/api/gog/login')
def gog_login():
    url = get_gog_auth_url(GOG_REDIRECT_URI)
    return redirect(url)

@app.route('/api/gog/callback')
def gog_callback():
    code = request.args.get('code')
    if not code:
        return "Missing code", 400
    token_data = exchange_code_for_token(code, GOG_REDIRECT_URI)
    if token_data:
        # 登录成功，重定向到首页，前端会刷新状态
        return redirect('/')
    else:
        return "Token exchange failed", 400

@app.route('/api/gog/status')
def gog_status():
    if load_gog_token():
        return jsonify({"authenticated": True, "account_name": get_gog_account_name() or "GOG User"})
    return jsonify({"authenticated": False})

@app.route('/api/gog/sync', methods=['POST'])
def sync_gog_library():
    if not load_gog_token():
        return jsonify({"success": False, "error": "Not logged in"}), 401
    games = get_gog_games()
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

@app.route('/api/gog/games')
def api_gog_games():
    limit = int(request.args.get('limit', 28))
    offset = int(request.args.get('offset', 0))
    search = request.args.get('search', '').strip()
    all_games = get_all_gog_games()
    if search:
        all_games = [g for g in all_games if search.lower() in g['name'].lower()]
    total = len(all_games)
    paged = all_games[offset:offset+limit]
    for g in paged:
        g['image_url'] = f"/images_gog/{g['game_id']}.jpg"
        g['id'] = g.pop('game_id')
    return jsonify({"games": paged, "total": total})

@app.route('/images_gog/<game_id>.jpg')
def gog_image(game_id):
    local_path = get_gog_image_path(game_id)
    if local_path.exists() and not is_image_valid(local_path):
        # 删除损坏的文件
        local_path.unlink()
    if not local_path.exists():
        conn = sqlite3.connect("gog_games.db")
        c = conn.cursor()
        c.execute("SELECT image_url FROM gog_games WHERE game_id = ?", (game_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            download_gog_image(row[0], game_id)
    if local_path.exists():
        return send_file(local_path, mimetype='image/jpeg')
    else:
        return "", 404

@app.route('/api/gog/sync_from_extension', methods=['POST'])
def gog_sync_from_extension():
    data = request.json
    games = data.get('games', [])
    if not games:
        return jsonify({"success": False, "error": "No games data"}), 400
    
    from gog_db import clear_gog_games, upsert_gog_game
    from cache_manager import download_gog_image
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

@app.route('/api/gog/count')
def gog_count():
    from gog_db import count_gog_games
    count = count_gog_games()
    return jsonify({"count": count})

# ==================== Cubejoy 相关路由 ====================
@app.route('/api/cubejoy/sync', methods=['POST'])
def cubejoy_sync():
    data = request.json
    games = data.get('games', [])
    if not games:
        return jsonify({"success": False, "error": "No games data"}), 400
    from cubejoy_db import clear_cubejoy_games, upsert_cubejoy_game
    from cache_manager import download_cubejoy_image
    clear_cubejoy_games()
    now = int(time.time())
    for game in games:
        game_id = str(game.get('game_id'))
        s_id = game.get('s_id', '')
        title = game.get('title', 'Unknown')
        image_url = game.get('image_url', '')
        if image_url:
            download_cubejoy_image(image_url, game_id)
        upsert_cubejoy_game(game_id, s_id, title, image_url, now)
    return jsonify({"success": True, "count": len(games)})

@app.route('/api/cubejoy/count')
def cubejoy_count():
    count = count_cubejoy_games()
    return jsonify({"count": count})

# 图片代理
@app.route('/images_cubejoy/<game_id>.jpg')
def cubejoy_image(game_id):
    local_path = get_cubejoy_image_path(game_id)
    if local_path.exists() and not is_image_valid(local_path):
        # 删除损坏的文件
        local_path.unlink()
    if not local_path.exists():
        conn = sqlite3.connect("cubejoy_games.db")
        c = conn.cursor()
        c.execute("SELECT image_url FROM cubejoy_games WHERE game_id = ?", (game_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            download_cubejoy_image(row[0], game_id)
    if local_path.exists():
        return send_file(local_path, mimetype='image/jpeg')
    else:
        return "", 404

# ==================== 启动 ====================
def open_browser():
    webbrowser.open('http://localhost:5000')

if __name__ == '__main__':
    Timer(1, open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=False)