import json
from core.config_db import init_config_db, get_all_config, set_all_config

# 初始化配置表
init_config_db()

DEFAULT_CONFIG = {
    "steamid": None,
    "api_key": None,
    "steam_path": None,
    "steamid_alt": None,
    "api_key_alt": None,
    "epic_client_id": "",
    "epic_client_secret": "",
    "steamgriddb_api_key": "",
}

def load_config():
    try:
        data = get_all_config()
        if not data:
            return DEFAULT_CONFIG.copy()
        for key, val in DEFAULT_CONFIG.items():
            if key not in data:
                data[key] = val
        return data
    except Exception as e:
        print(f"Load config error: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(data):
    try:
        set_all_config(data)
    except Exception as e:
        print(f"Save config error: {e}")

config = load_config()