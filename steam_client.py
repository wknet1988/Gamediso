import requests
import vdf
import os
import urllib3
import time
import sqlite3
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, parse_qs
from database import DB_PATH, upsert_game, clear_shelves, add_shelf, add_game_to_shelf
from cache_manager import get_cached_image_path, download_image

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------- OpenID 登录部分 ----------
def get_steam_login_url(return_to: str) -> str:
    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': return_to,
        'openid.realm': 'http://localhost:5000',
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }
    url = 'https://steamcommunity.com/openid/login'
    response = requests.get(url, params=params, allow_redirects=False, verify=False)
    return response.headers['Location']

def validate_steam_callback(callback_url: str) -> Optional[str]:
    parsed = urlparse(callback_url)
    query = parse_qs(parsed.query)
    if 'openid.claimed_id' in query:
        claimed_id = query['openid.claimed_id'][0]
        if '/id/' in claimed_id:
            steamid = claimed_id.split('/')[-1]
            return steamid
    return None

# ---------- 获取自己拥有的游戏 ----------
def fetch_owned_games(api_key: str, steamid: str) -> List[Dict[str, Any]]:
    url = 'https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/'
    params = {
        'key': api_key,
        'steamid': steamid,
        'include_appinfo': True,
        'include_played_free_games': True,
        'format': 'json'
    }
    resp = requests.get(url, params=params, verify=False)
    data = resp.json()
    games = data.get('response', {}).get('games', [])
    result = []
    for g in games:
        appid = g['appid']
        name = g.get('name', 'Unknown')
        header_url = f'https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}/header.jpg'
        result.append({
            'appid': appid,
            'name': name,
            'header_url': header_url,
            'type': 'owned'
        })
    return result

# ---------- 获取家庭组信息 ----------
def get_family_group_for_user(api_key: str, steamid: str) -> Optional[Dict]:
    url = 'https://api.steampowered.com/IFamilyGroupsService/GetFamilyGroupForUser/v1/'
    params = {
        'key': api_key,
        'steamid': steamid,
        'include_family_group_response': True,
    }
    resp = requests.get(url, params=params, verify=False)
    # ----- 修正缩进开始 -----
    if resp.status_code != 200:
        if resp.status_code != 401:
            print(f"获取家庭组信息失败: {resp.status_code}")
        return None
    # ----- 修正缩进结束 -----
    data = resp.json()
    response = data.get('response', {})
    if 'family_groupid' not in response:
        print("用户未加入任何家庭组")
        return None
    family_group = response.get('family_group', {})
    members = family_group.get('members', [])
    member_steamids = [m['steamid'] for m in members]
    names_map = {}
    if member_steamids:
        name_url = 'https://api.steampowered.com/IPlayerService/GetPlayerLinkDetails/v1/'
        name_params = {'key': api_key}
        for idx, sid in enumerate(member_steamids):
            name_params[f'steamids[{idx}]'] = sid
        name_resp = requests.get(name_url, params=name_params, verify=False)
        if name_resp.status_code == 200:
            name_data = name_resp.json()
            accounts = name_data.get('response', {}).get('accounts', [])
            for acc in accounts:
                names_map[acc['public_data']['steamid']] = acc['public_data']['persona_name']
    for m in members:
        m['userName'] = names_map.get(m['steamid'], 'Unknown')
    return {
        'family_groupid': response['family_groupid'],
        'family_name': family_group.get('name', ''),
        'family_member': members,
        'steamIdtoName': names_map
    }

# ---------- 获取家庭共享游戏 ----------
def fetch_family_shared_games(api_key: str, family_groupid: str) -> List[Dict[str, Any]]:
    url = 'https://api.steampowered.com/IFamilyGroupsService/GetSharedLibraryApps/v1/'
    params = {
        'key': api_key,
        'family_groupid': family_groupid,
        'include_own': True,
        'include_excluded': False,
        'include_non_games': False,
    }
    resp = requests.get(url, params=params, verify=False)
    if resp.status_code != 200:
        print(f"获取家庭共享游戏失败: {resp.status_code}")
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
                'rt_time_acquired': app.get('rt_time_acquired', 0),
                'type': 'shared'
            })
    return result

# ---------- 解析 Steam 自定义列表 ----------
def parse_steam_groups(steam_install_path: str, steamid: str) -> Dict[str, List[int]]:
    vdf_path = os.path.join(steam_install_path, 'userdata', steamid, '7', 'remote', 'sharedconfig.vdf')
    if not os.path.exists(vdf_path):
        return {}
    with open(vdf_path, 'r', encoding='utf-8') as f:
        data = vdf.load(f)
    groups = {}
    favorites = data.get('UserLocalConfigStore', {}).get('favorites', {}).get('apps', [])
    if favorites:
        groups['我的最爱'] = favorites
    game_groups = data.get('UserLocalConfigStore', {}).get('Software', {}).get('Valve', {}).get('Steam', {}).get('Groups', {})
    for group_name, group_data in game_groups.items():
        apps = group_data.get('apps', [])
        if apps:
            groups[group_name] = apps
    return groups

# ---------- 刷新 Steam 自定义货架 ----------
def refresh_shelves_from_steam(steam_path: str, steamid: str) -> bool:
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

# ---------- 使用 access_token 获取家庭组 ----------
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

# ---------- 使用 access_token 获取家庭共享游戏 ----------
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

# ---------- 刷新游戏库（含进度跟踪） ----------
def refresh_games_library(steamid, api_key, steam_path=None, force=False, task_id=None):
    if not steamid or not api_key:
        return False

    if task_id:
        from core.task_manager import task_manager
        task_manager.update_task(task_id, 5, '检查数据库...')

    conn = sqlite3.connect(DB_PATH, timeout=10)
    c = conn.cursor()
    c.execute("SELECT MAX(last_updated) FROM games")
    row = c.fetchone()
    last = row[0] if row[0] else 0
    conn.close()

    now = int(time.time())
    if not force and (now - last) < 86400:
        if task_id:
            task_manager.update_task(task_id, 100, '已是最新，无需同步')
            task_manager.finish_task(task_id)
        return True

    try:
        if task_id:
            task_manager.update_task(task_id, 10, '获取自有游戏列表...')
        owned_games = fetch_owned_games(api_key, steamid)

        if task_id:
            task_manager.update_task(task_id, 30, '获取家庭共享游戏...')
        family_info = get_family_group_for_user(api_key, steamid)
        family_games = []
        if family_info:
            family_games = fetch_family_shared_games(api_key, family_info['family_groupid'])

        # 1. 获取本地已有 appid 集合
        conn = sqlite3.connect(DB_PATH, timeout=10)
        c = conn.cursor()
        c.execute("SELECT appid FROM games")
        local_ids = {row[0] for row in c.fetchall()}
        conn.close()

        # 2. 构建远程游戏字典（去重，优先 owned）
        owned_appids = {g['appid'] for g in owned_games}
        remote_games = {}
        for g in owned_games:
            remote_games[g['appid']] = {
                'name': g['name'],
                'header_url': g['header_url'],
                'type': 'owned'
            }
        for g in family_games:
            appid = g['appid']
            if appid not in remote_games:  # 如果 owned 已有，不覆盖
                remote_games[appid] = {
                    'name': g['name'],
                    'header_url': g['header_url'],
                    'type': 'shared'
                }

        remote_ids = set(remote_games.keys())
        total = len(remote_ids)
        processed = 0

        if task_id:
            task_manager.update_task(task_id, 50, f'开始同步 (共 {total} 款)...')

        # 3. 更新或插入远程游戏（仅新增，已有跳过）
        for appid, game in remote_games.items():
            if appid in local_ids:  # 已存在，跳过
                processed += 1
                if task_id and processed % 50 == 0:
                    progress = 10 + int((processed / total) * 40)
                    task_manager.update_task(task_id, min(progress, 90), f'已检查 {processed}/{total}')
                continue

        # 新游戏，插入并下载图片
        upsert_game(appid, game['name'], game['header_url'], now, game['type'])
        if not get_cached_image_path(appid).exists():
            download_image(game['header_url'], appid)
        processed += 1
        if task_id and processed % 10 == 0:
            progress = 10 + int((processed / total) * 40)
            task_manager.update_task(task_id, min(progress, 90), f'已处理 {processed}/{total}')

        # 4. 删除本地多余的游戏
        to_delete = local_ids - remote_ids
        if to_delete:
            if task_id:
                task_manager.update_task(task_id, 92, f'删除本地多余游戏 ({len(to_delete)} 款)')
            placeholders = ','.join(['?'] * len(to_delete))
            conn = sqlite3.connect(DB_PATH, timeout=10)
            c = conn.cursor()
            c.execute(f"DELETE FROM games WHERE appid IN ({placeholders})", tuple(to_delete))
            conn.commit()
            conn.close()
            if task_id:
                task_manager.update_task(task_id, 95, f'已删除 {len(to_delete)} 款游戏')

        if task_id:
            task_manager.update_task(task_id, 96, '更新自定义列表...')
        if steam_path:
            refresh_shelves_from_steam(steam_path, steamid)

        if task_id:
            task_manager.update_task(task_id, 100, f'同步完成 (保留 {total} 款，删除 {len(to_delete)} 款)')
            task_manager.finish_task(task_id)
        return True
    except Exception as e:
        if task_id:
            task_manager.update_task(task_id, 100, f'同步失败: {str(e)}')
            task_manager.finish_task(task_id, str(e))
        print(f"刷新游戏库失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
def refresh_games_library_alt(steamid, api_key, force=False, task_id=None):
    """同步副号 Steam 游戏库，标记为 alt"""
    if not steamid or not api_key:
        return False

    if task_id:
        from core.task_manager import task_manager
        task_manager.update_task(task_id, 5, '检查副号数据库...')

    # 完全复用主号逻辑，但 game_type 为 'alt'
    conn = sqlite3.connect(DB_PATH, timeout=10)
    c = conn.cursor()
    c.execute("SELECT MAX(last_updated) FROM games WHERE type = 'alt'")
    row = c.fetchone()
    last = row[0] if row[0] else 0
    conn.close()

    now = int(time.time())
    if not force and (now - last) < 86400:
        if task_id:
            task_manager.update_task(task_id, 100, '副号已是最新，无需同步')
            task_manager.finish_task(task_id)
        return True

    try:
        if task_id:
            task_manager.update_task(task_id, 10, '获取副号游戏列表...')
        owned_games = fetch_owned_games(api_key, steamid)

        # 获取本地已有 appid（只考虑主号和副号，避免重复）
        conn = sqlite3.connect(DB_PATH, timeout=10)
        c = conn.cursor()
        c.execute("SELECT appid FROM games WHERE type IN ('owned', 'alt')")
        local_ids = {row[0] for row in c.fetchall()}
        conn.close()

        remote_ids = {g['appid'] for g in owned_games}
        total = len(remote_ids)
        processed = 0

        if task_id:
            task_manager.update_task(task_id, 50, f'开始同步副号 (共 {total} 款)...')

        # 处理副号游戏（仅新增，已有跳过）
        for game in owned_games:
            appid = game['appid']
            if appid in local_ids:  # 已存在（主号或副号），跳过
                processed += 1
                if task_id and processed % 50 == 0:
                    progress = 50 + int((processed / total) * 40)
                    task_manager.update_task(task_id, min(progress, 90), f'已检查 {processed}/{total}')
                continue

        # 新游戏，插入并下载图片（标记为 alt）
        upsert_game(appid, game['name'], game['header_url'], now, 'alt')
        if not get_cached_image_path(appid).exists():
            download_image(game['header_url'], appid)
        processed += 1
        if task_id and processed % 10 == 0:
            progress = 50 + int((processed / total) * 40)
            task_manager.update_task(task_id, min(progress, 90), f'已处理 {processed}/{total}')

        if task_id:
            task_manager.update_task(task_id, 95, '副号同步完成')
            task_manager.finish_task(task_id)
        return True
    except Exception as e:
        if task_id:
            task_manager.update_task(task_id, 100, f'副号同步失败: {str(e)}')
            task_manager.finish_task(task_id, str(e))
        print(f"副号同步失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    
# ---------- 同步自有游戏（主号） ----------
def sync_owned_games(steamid, api_key, force=False, task_id=None):
    """同步主号自有游戏，类型为 'owned'，优先级最高"""
    if not steamid or not api_key:
        return False

    if task_id:
        from core.task_manager import task_manager
        task_manager.update_task(task_id, 5, '检查主号数据库...')

    now = int(time.time())
    try:
        if task_id:
            task_manager.update_task(task_id, 10, '获取主号游戏列表...')
        owned_games = fetch_owned_games(api_key, steamid)

        # 获取本地主号游戏 ID (type='owned')
        conn = sqlite3.connect(DB_PATH, timeout=10)
        c = conn.cursor()
        c.execute("SELECT appid FROM games WHERE type = 'owned'")
        local_owned_ids = {row[0] for row in c.fetchall()}
        conn.close()

        remote_ids = {g['appid'] for g in owned_games}
        total = len(remote_ids)
        processed = 0

        if task_id:
            task_manager.update_task(task_id, 50, f'开始同步主号 (共 {total} 款)...')

        # 插入或更新主号游戏（如果远程有，则设为 'owned'，覆盖其他类型）
        for game in owned_games:
            appid = game['appid']
            # 检查是否已存在且类型为 'owned'
            conn = sqlite3.connect(DB_PATH, timeout=10)
            c = conn.cursor()
            c.execute("SELECT type FROM games WHERE appid = ?", (appid,))
            row = c.fetchone()
            if row and row[0] == 'owned':
                # 已存在且类型正确，跳过
                conn.close()
                processed += 1
                if task_id and processed % 10 == 0:
                    progress = 50 + int((processed / total) * 40)
                    task_manager.update_task(task_id, min(progress, 90), f'已检查 {processed}/{total}')
                continue
            conn.close()
            # 否则插入或更新为 'owned'
            upsert_game(appid, game['name'], game['header_url'], now, 'owned')
            if not get_cached_image_path(appid).exists():
                download_image(game['header_url'], appid)
            processed += 1
            if task_id and processed % 10 == 0:
                progress = 50 + int((processed / total) * 40)
                task_manager.update_task(task_id, min(progress, 90), f'已处理 {processed}/{total}')

        # 删除主号本地多余的游戏（仅删除 type='owned' 且不在远程列表中的）
        to_delete_owned = local_owned_ids - remote_ids
        if to_delete_owned:
            placeholders = ','.join(['?'] * len(to_delete_owned))
            conn = sqlite3.connect(DB_PATH, timeout=10)
            c = conn.cursor()
            c.execute(f"DELETE FROM games WHERE appid IN ({placeholders}) AND type = 'owned'", tuple(to_delete_owned))
            conn.commit()
            conn.close()
            if task_id:
                task_manager.update_task(task_id, 92, f'删除主号多余游戏 ({len(to_delete_owned)} 款)')

        if task_id:
            task_manager.update_task(task_id, 100, f'主号同步完成 (保留 {len(remote_ids)} 款，删除 {len(to_delete_owned)} 款)')
            task_manager.finish_task(task_id)
        return True
    except Exception as e:
        if task_id:
            task_manager.update_task(task_id, 100, f'主号同步失败: {str(e)}')
            task_manager.finish_task(task_id, str(e))
        print(f"主号同步失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ---------- 同步家庭组共享游戏 ----------
def sync_family_games(steamid, api_key, force=False, task_id=None):
    """同步家庭组共享游戏，类型为 'shared'，优先级次于主号"""
    if not steamid or not api_key:
        return False

    if task_id:
        from core.task_manager import task_manager
        task_manager.update_task(task_id, 5, '检查家庭组数据库...')

    now = int(time.time())
    try:
        if task_id:
            task_manager.update_task(task_id, 10, '获取家庭组游戏列表...')
        family_info = get_family_group_for_user(api_key, steamid)
        if not family_info:
            if task_id:
                task_manager.update_task(task_id, 100, '未加入家庭组或获取失败')
                task_manager.finish_task(task_id)
            return False
        family_games = fetch_family_shared_games(api_key, family_info['family_groupid'])

        # 获取本地家庭组游戏 ID (type='shared')
        conn = sqlite3.connect(DB_PATH, timeout=10)
        c = conn.cursor()
        c.execute("SELECT appid FROM games WHERE type = 'shared'")
        local_shared_ids = {row[0] for row in c.fetchall()}
        conn.close()

        remote_ids = {g['appid'] for g in family_games}
        total = len(remote_ids)
        processed = 0

        if task_id:
            task_manager.update_task(task_id, 50, f'开始同步家庭组 (共 {total} 款)...')

        for game in family_games:
            appid = game['appid']
            conn = sqlite3.connect(DB_PATH, timeout=10)
            c = conn.cursor()
            c.execute("SELECT type FROM games WHERE appid = ?", (appid,))
            row = c.fetchone()
            if row and row[0] in ('owned', 'shared'):
                # 已存在且类型为 owned 或 shared，跳过（owned 优先）
                conn.close()
                processed += 1
                if task_id and processed % 10 == 0:
                    progress = 50 + int((processed / total) * 40)
                    task_manager.update_task(task_id, min(progress, 90), f'已检查 {processed}/{total}')
                continue
            conn.close()
            # 插入或更新为 'shared'
            upsert_game(appid, game['name'], game['header_url'], now, 'shared')
            if not get_cached_image_path(appid).exists():
                download_image(game['header_url'], appid)
            processed += 1
            if task_id and processed % 10 == 0:
                progress = 50 + int((processed / total) * 40)
                task_manager.update_task(task_id, min(progress, 90), f'已处理 {processed}/{total}')
            conn.close()

        # 删除家庭组本地多余的游戏（仅删除 type='shared' 且不在远程列表中的）
        to_delete_shared = local_shared_ids - remote_ids
        if to_delete_shared:
            placeholders = ','.join(['?'] * len(to_delete_shared))
            conn = sqlite3.connect(DB_PATH, timeout=10)
            c = conn.cursor()
            c.execute(f"DELETE FROM games WHERE appid IN ({placeholders}) AND type = 'shared'", tuple(to_delete_shared))
            conn.commit()
            conn.close()
            if task_id:
                task_manager.update_task(task_id, 92, f'删除家庭组多余游戏 ({len(to_delete_shared)} 款)')

        if task_id:
            task_manager.update_task(task_id, 100, f'家庭组同步完成 (保留 {len(remote_ids)} 款，删除 {len(to_delete_shared)} 款)')
            task_manager.finish_task(task_id)
        return True
    except Exception as e:
        if task_id:
            task_manager.update_task(task_id, 100, f'家庭组同步失败: {str(e)}')
            task_manager.finish_task(task_id, str(e))
        print(f"家庭组同步失败: {e}")
        import traceback
        traceback.print_exc()
        return False

# ---------- 同步副号游戏 ----------
def sync_alt_games(steamid, api_key, force=False, task_id=None):
    """同步副号游戏，类型为 'alt'，优先级最低"""
    if not steamid or not api_key:
        return False

    if task_id:
        from core.task_manager import task_manager
        task_manager.update_task(task_id, 5, '检查副号数据库...')

    now = int(time.time())
    try:
        if task_id:
            task_manager.update_task(task_id, 10, '获取副号游戏列表...')
        owned_games = fetch_owned_games(api_key, steamid)

        # 获取本地副号游戏 ID (type='alt')
        conn = sqlite3.connect(DB_PATH, timeout=10)
        c = conn.cursor()
        c.execute("SELECT appid FROM games WHERE type = 'alt'")
        local_alt_ids = {row[0] for row in c.fetchall()}
        conn.close()

        remote_ids = {g['appid'] for g in owned_games}
        total = len(remote_ids)
        processed = 0

        if task_id:
            task_manager.update_task(task_id, 50, f'开始同步副号 (共 {total} 款)...')

        for game in owned_games:
            appid = game['appid']
            conn = sqlite3.connect(DB_PATH, timeout=10)
            c = conn.cursor()
            c.execute("SELECT type FROM games WHERE appid = ?", (appid,))
            row = c.fetchone()
            if row and row[0] in ('owned', 'shared', 'alt'):
                # 已存在且类型为 owned/shared/alt，跳过（更高优先级已覆盖）
                conn.close()
                processed += 1
                if task_id and processed % 10 == 0:
                    progress = 50 + int((processed / total) * 40)
                    task_manager.update_task(task_id, min(progress, 90), f'已检查 {processed}/{total}')
                continue
            conn.close()
            # 插入或更新为 'alt'
            upsert_game(appid, game['name'], game['header_url'], now, 'alt')
            if not get_cached_image_path(appid).exists():
                download_image(game['header_url'], appid)
            processed += 1
            if task_id and processed % 10 == 0:
                progress = 50 + int((processed / total) * 40)
                task_manager.update_task(task_id, min(progress, 90), f'已处理 {processed}/{total}')
            conn.close()

        # 删除副号本地多余的游戏（仅删除 type='alt' 且不在远程列表中的）
        to_delete_alt = local_alt_ids - remote_ids
        if to_delete_alt:
            placeholders = ','.join(['?'] * len(to_delete_alt))
            conn = sqlite3.connect(DB_PATH, timeout=10)
            c = conn.cursor()
            c.execute(f"DELETE FROM games WHERE appid IN ({placeholders}) AND type = 'alt'", tuple(to_delete_alt))
            conn.commit()
            conn.close()
            if task_id:
                task_manager.update_task(task_id, 92, f'删除副号多余游戏 ({len(to_delete_alt)} 款)')

        if task_id:
            task_manager.update_task(task_id, 100, f'副号同步完成 (保留 {len(remote_ids)} 款，删除 {len(to_delete_alt)} 款)')
            task_manager.finish_task(task_id)
        return True
    except Exception as e:
        if task_id:
            task_manager.update_task(task_id, 100, f'副号同步失败: {str(e)}')
            task_manager.finish_task(task_id, str(e))
        print(f"副号同步失败: {e}")
        import traceback
        traceback.print_exc()
        return False
