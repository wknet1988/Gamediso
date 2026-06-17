import requests
import vdf
import os
import urllib3
from typing import Optional, List, Dict, Any
from urllib.parse import urlparse, parse_qs

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ---------- OpenID 登录部分（原有） ----------
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

# ---------- 新增：获取家庭组信息 ----------
def get_family_group_for_user(api_key: str, steamid: str) -> Optional[Dict]:
    """通过 Steam Web API 获取用户所在的家庭组信息"""
    url = 'https://api.steampowered.com/IFamilyGroupsService/GetFamilyGroupForUser/v1/'
    params = {
        'key': api_key,
        'steamid': steamid,
        'include_family_group_response': True,
    }
    resp = requests.get(url, params=params, verify=False)
    if resp.status_code != 200:
        print(f"获取家庭组信息失败: {resp.status_code}")
        return None
    data = resp.json()
    response = data.get('response', {})
    if 'family_groupid' not in response:
        print("用户未加入任何家庭组")
        return None
    family_group = response.get('family_group', {})
    members = family_group.get('members', [])
    # 获取成员昵称
    member_steamids = [m['steamid'] for m in members]
    names_map = {}
    if member_steamids:
        # 调用 GetPlayerLinkDetails 批量获取昵称
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
    # 将昵称添加到 members 中
    for m in members:
        m['userName'] = names_map.get(m['steamid'], 'Unknown')
    return {
        'family_groupid': response['family_groupid'],
        'family_name': family_group.get('name', ''),
        'family_member': members,
        'steamIdtoName': names_map
    }

# ---------- 新增：获取家庭组共享游戏列表 ----------
def fetch_family_shared_games(api_key: str, family_groupid: str) -> List[Dict[str, Any]]:
    """获取家庭组内所有共享游戏（包括成员拥有的）"""
    url = 'https://api.steampowered.com/IFamilyGroupsService/GetSharedLibraryApps/v1/'
    params = {
        'key': api_key,
        'family_groupid': family_groupid,
        'include_own': True,        # 包含成员自己拥有的游戏
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
        # exclude_reason == 0 表示可共享
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

# ---------- 原有的 parse_steam_groups 用于自定义列表 ----------
def parse_steam_groups(steam_install_path: str, steamid: str) -> Dict[str, List[int]]:
    # 保持不变，解析 sharedconfig.vdf 获取用户自定义货架和我的最爱
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