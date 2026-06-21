import os
import json

CONFIG_FILE = "config.json"

def load_config():
    """加载 config.json，如果不存在或格式错误则返回默认配置"""
    default_config = {
        "steamid": None,
        "api_key": None,
        "steam_path": None,
        "steamid_alt": None,
        "api_key_alt": None,
        "epic_client_id": "",
        "epic_client_secret": "",
        "steamgriddb_api_key": "",
    }
    if not os.path.exists(CONFIG_FILE):
        return default_config
    try:
        with open(CONFIG_FILE, 'r') as f:
            content = f.read().strip()
            if not content:
                return default_config
            data = json.loads(content)
            # 合并默认值，确保所有键存在
            for key, val in default_config.items():
                if key not in data:
                    data[key] = val
            return data
    except (json.JSONDecodeError, IOError):
        return default_config

def save_config(data):
    """保存配置到 config.json"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# 全局配置实例（单例）
config = load_config()