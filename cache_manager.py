import os
import requests
from pathlib import Path
import imghdr  # 标准库，用于检测图片类型

# 尝试导入 PIL（如果已安装）
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    # 可选：打印提示，但非必需
    # print("Pillow (PIL) not installed. Image validation will be limited to file size and imghdr.")

CACHE_DIR = Path("cache/images")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ========== 图片有效性检测 ==========
def is_image_valid(file_path):
    """检查图片文件是否有效（大小、类型、完整性）"""
    if not file_path.exists():
        return False
    # 1. 文件大小至少 1KB（避免空文件或极小的无效文件）
    if file_path.stat().st_size < 1024:
        return False
    # 2. 使用 imghdr 检测图片类型
    img_type = imghdr.what(file_path)
    if img_type is None:
        return False
    # 3. 如果 PIL 可用，进一步验证完整性
    if HAS_PIL:
        try:
            with Image.open(file_path) as img:
                img.verify()  # 验证图片完整性
            return True
        except Exception:
            return False
    return True  # 没有 PIL 时，只通过 imghdr 检测

def download_with_validation(url, file_path, max_retries=1):
    """下载图片到临时文件，验证有效后替换原文件"""
    for attempt in range(max_retries + 1):
        try:
            # 使用临时文件，避免写入过程中失败导致残留
            temp_path = file_path.with_suffix('.tmp')
            resp = requests.get(url, stream=True, timeout=10, verify=False)
            if resp.status_code != 200:
                if attempt < max_retries:
                    continue
                else:
                    return False
            # 写入临时文件
            with open(temp_path, 'wb') as f:
                for chunk in resp.iter_content(1024):
                    f.write(chunk)
            # 验证临时文件
            if is_image_valid(temp_path):
                # 替换原文件
                if file_path.exists():
                    file_path.unlink()
                temp_path.rename(file_path)
                return True
            else:
                # 删除无效临时文件
                temp_path.unlink()
                print(f"下载的图片无效，已删除: {url}")
                if attempt < max_retries:
                    continue
                else:
                    return False
        except Exception as e:
            print(f"下载异常: {url}, {e}")
            if attempt < max_retries:
                continue
            else:
                return False
    return False

# ========== 原有的缓存路径函数 ==========
def get_cached_image_path(appid: int) -> Path:
    """返回本地缓存图片路径（即使文件可能不存在）"""
    return CACHE_DIR / f"{appid}_header.jpg"

def get_image_local_url(appid: int) -> str:
    """返回 Flask 可访问的本地图片 URL（代理路由）"""
    return f"/images/{appid}.jpg"

def get_platform_image_path(platform: str, game_id: str):
    """platform: 'steam' or 'epic'"""
    base_dir = CACHE_DIR / platform
    base_dir.mkdir(parents=True, exist_ok=True)
    return base_dir / f"{game_id}.jpg"

def get_gog_image_path(game_id: str):
    gog_cache_dir = CACHE_DIR / "gog"
    gog_cache_dir.mkdir(parents=True, exist_ok=True)
    return gog_cache_dir / f"{game_id}.jpg"

def get_cubejoy_image_path(game_id: str):
    cubejoy_cache_dir = CACHE_DIR / "cubejoy"
    cubejoy_cache_dir.mkdir(parents=True, exist_ok=True)
    return cubejoy_cache_dir / f"{game_id}.jpg"

# ========== 各平台下载函数（已增加验证） ==========
def download_image(url: str, appid: int) -> bool:
    """Steam 专用图片下载"""
    local_path = get_cached_image_path(appid)
    # 如果存在但无效，删除
    if local_path.exists() and not is_image_valid(local_path):
        local_path.unlink()
    if local_path.exists():
        return True
    return download_with_validation(url, local_path)

def download_platform_image(url: str, platform: str, game_id: str) -> bool:
    """通用平台图片下载（Epic等）"""
    if not url:
        return False
    local_path = get_platform_image_path(platform, game_id)
    if local_path.exists() and not is_image_valid(local_path):
        local_path.unlink()
    if local_path.exists():
        return True
    # 添加 User-Agent 头部
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    return download_with_validation(url, local_path, headers=headers)

def download_gog_image(url: str, game_id: str) -> bool:
    """GOG 专用图片下载"""
    local_path = get_gog_image_path(game_id)
    if local_path.exists() and not is_image_valid(local_path):
        local_path.unlink()
    if local_path.exists():
        return True
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    return download_with_validation(url, local_path, headers=headers)

def download_cubejoy_image(url: str, game_id: str) -> bool:
    """Cubejoy 专用图片下载"""
    if not url:
        return False
    # 如果 URL 是相对路径（以 // 开头），补全协议
    if url.startswith('//'):
        url = 'https:' + url
    local_path = get_cubejoy_image_path(game_id)
    if local_path.exists() and not is_image_valid(local_path):
        local_path.unlink()
    if local_path.exists():
        return True
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    return download_with_validation(url, local_path, headers=headers)