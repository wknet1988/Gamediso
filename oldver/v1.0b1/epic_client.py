import requests
import urllib3
from typing import Optional, Dict, List, Any

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EPIC_AUTHORIZE_URL = "https://www.epicgames.com/id/authorize"
EPIC_TOKEN_URL = "https://api.epicgames.dev/epic/oauth/v1/token"
EPIC_GRAPHQL_URL = "https://graphql.epicgames.com/graphql"

def get_epic_auth_url(client_id: str, redirect_uri: str) -> str:
    from urllib.parse import urlencode
    params = {
        "client_id": client_id,
        "response_type": "code",
        "scope": "basic profile",
        "redirect_uri": redirect_uri,
    }
    return f"{EPIC_AUTHORIZE_URL}?{urlencode(params)}"

def exchange_code_for_token(client_id: str, client_secret: str, code: str, redirect_uri: str) -> Optional[Dict]:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
    }
    auth = (client_id, client_secret)
    resp = requests.post(EPIC_TOKEN_URL, data=data, auth=auth, verify=False)
    if resp.status_code == 200:
        return resp.json()
    return None

def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> Optional[Dict]:
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    auth = (client_id, client_secret)
    resp = requests.post(EPIC_TOKEN_URL, data=data, auth=auth, verify=False)
    if resp.status_code == 200:
        return resp.json()
    return None

def fetch_epic_games(access_token: str) -> List[Dict[str, Any]]:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    query = """
    {
        currentUser {
            ownedGames {
                elements {
                    id
                    title
                    sandbox
                    productSlug
                }
            }
        }
    }
    """
    payload = {"query": query}
    resp = requests.post(EPIC_GRAPHQL_URL, json=payload, headers=headers, verify=False)
    if resp.status_code != 200:
        print(f"Epic GraphQL 错误: {resp.status_code}")
        return []
    data = resp.json()
    owned_games = data.get("data", {}).get("currentUser", {}).get("ownedGames", {}).get("elements", [])
    result = []
    for game in owned_games:
        game_id = game['id']
        title = game['title']
        sandbox = game.get('sandbox', '')
        image_url = f"https://cdn2.epicgames.com/{sandbox}/offer/{game_id}.jpg" if sandbox else ""
        result.append({
            "game_id": game_id,
            "name": title,
            "header_url": image_url,
            "sandbox": sandbox
        })
    return result