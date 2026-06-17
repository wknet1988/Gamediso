import requests
import urllib3
import json
from typing import Optional, Dict

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

EPIC_TOKEN_URL = "https://api.epicgames.dev/epic/oauth/v1/token"
EPIC_DEVICE_AUTH_URL = "https://api.epicgames.dev/epic/oauth/v1/deviceAuth"

def exchange_code_for_token(client_id: str, client_secret: str, code: str, redirect_uri: str) -> Optional[Dict]:
    """用授权码换取 access_token 和 refresh_token"""
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
    """用 refresh_token 刷新 access_token"""
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    auth = (client_id, client_secret)
    resp = requests.post(EPIC_TOKEN_URL, data=data, auth=auth, verify=False)
    if resp.status_code == 200:
        return resp.json()
    return None

def create_device_auth(access_token: str, client_id: str) -> Optional[Dict]:
    """使用 access_token 创建设备授权凭证（长期有效）"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "client_id": client_id,
    }
    resp = requests.post(EPIC_DEVICE_AUTH_URL, json=payload, headers=headers, verify=False)
    if resp.status_code == 200:
        return resp.json()
    return None

def login_with_device_auth(client_id: str, device_id: str, secret: str) -> Optional[Dict]:
    """使用设备凭证登录，获取 access_token"""
    data = {
        "grant_type": "device_auth",
        "device_id": device_id,
        "secret": secret,
    }
    auth = (client_id, "")
    resp = requests.post(EPIC_TOKEN_URL, data=data, auth=auth, verify=False)
    if resp.status_code == 200:
        return resp.json()
    return None