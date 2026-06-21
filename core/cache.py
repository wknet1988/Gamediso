import os
import requests
import time
import imghdr
from pathlib import Path

CACHE_DIR = Path("cache/images")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ---------- 辅助函数 ----------
def is_image_valid(file_path: Path) -> bool:
    if not file_path.exists() or file_path.stat().st_size < 1024:
        return False
    return imghdr.what(file_path) is not None

def get_cache_path(platform: str, game_id: str) -> Path:
    platform_dir = CACHE_DIR / platform
    platform_dir.mkdir(parents=True, exist_ok=True)
    return platform_dir / f"{game_id}.jpg"

def download_with_validation(url: str, file_path: Path, max_retries: int = 1) -> bool:
    """下载并校验图片，支持重试"""
    for attempt in range(max_retries + 1):
        try:
            # 临时文件
            temp_path = file_path.with_suffix('.tmp')
            resp = requests.get(url, stream=True, timeout=10, verify=False)
            if resp.status_code != 200:
                if attempt < max_retries:
                    time.sleep(1)
                    continue
                return False
            with open(temp_path, 'wb') as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            if is_image_valid(temp_path):
                temp_path.rename(file_path)
                return True
            else:
                temp_path.unlink()
                if attempt < max_retries:
                    time.sleep(1)
                    continue
                return False
        except Exception:
            if attempt < max_retries:
                time.sleep(1)
                continue
            return False
    return False

# ---------- 各平台下载函数 ----------
def download_image(url: str, appid: int) -> bool:
    local_path = get_cache_path('steam', str(appid))
    if local_path.exists() and is_image_valid(local_path):
        return True
    if local_path.exists():
        local_path.unlink()
    return download_with_validation(url, local_path, max_retries=2)

def download_platform_image(url: str, platform: str, game_id: str) -> bool:
    if not url:
        return False
    if url.startswith('//'):
        url = 'https:' + url
    local_path = get_cache_path(platform, game_id)
    if local_path.exists() and is_image_valid(local_path):
        return True
    if local_path.exists():
        local_path.unlink()
    # Epic 需要 Referer
    headers = {}
    if platform == 'epic':
        headers['Referer'] = 'https://www.epicgames.com/'
    # 因为 download_with_validation 不支持 headers，我们在外层处理
    # 但为了兼容，可以修改 download_with_validation 支持 headers，或直接在此处实现下载
    # 简便起见，我们在这里直接用 requests.get 带 headers，并复用校验逻辑
    for attempt in range(3):
        try:
            resp = requests.get(url, stream=True, timeout=10, headers=headers, verify=False)
            if resp.status_code != 200:
                time.sleep(1)
                continue
            temp_path = local_path.with_suffix('.tmp')
            with open(temp_path, 'wb') as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            if is_image_valid(temp_path):
                temp_path.rename(local_path)
                return True
            else:
                temp_path.unlink()
                time.sleep(1)
        except Exception:
            time.sleep(1)
            continue
    return False

def download_gog_image(url: str, game_id: str) -> bool:
    return download_platform_image(url, 'gog', game_id)

def download_cubejoy_image(url: str, game_id: str) -> bool:
    if url and url.startswith('//'):
        url = 'https:' + url
    return download_platform_image(url, 'cubejoy', game_id)

# 兼容旧函数
def get_cached_image_path(appid: int) -> Path:
    return get_cache_path('steam', str(appid))

def get_platform_image_path(platform: str, game_id: str) -> Path:
    return get_cache_path(platform, game_id)

def get_gog_image_path(game_id: str) -> Path:
    return get_cache_path('gog', game_id)

def get_cubejoy_image_path(game_id: str) -> Path:
    return get_cache_path('cubejoy', game_id)

def download_image_from_steamgriddb(url: str, platform: str, game_id: str) -> bool:
    """从 SteamGridDB 下载图片到缓存"""
    if not url:
        return False
    # 如果 URL 是相对路径，补全协议
    if url.startswith('//'):
        url = 'https:' + url
    local_path = get_platform_image_path(platform, game_id)
    if local_path.exists() and is_image_valid(local_path):
        return True
    if local_path.exists():
        local_path.unlink()
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    for attempt in range(3):
        try:
            resp = requests.get(url, stream=True, timeout=15, headers=headers, verify=False)
            if resp.status_code == 200:
                temp_path = local_path.with_suffix('.tmp')
                with open(temp_path, 'wb') as f:
                    for chunk in resp.iter_content(1024):
                        f.write(chunk)
                if is_image_valid(temp_path):
                    temp_path.rename(local_path)
                    return True
                else:
                    temp_path.unlink()
            time.sleep(1)
        except Exception:
            time.sleep(1)
    return False