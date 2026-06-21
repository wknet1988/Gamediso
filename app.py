import os
import webbrowser
from threading import Timer
from flask import Flask, request, session, redirect, render_template, send_file, jsonify
from flask_cors import CORS
from blueprints.games import games_bp
from blueprints.images import images_bp
from blueprints.platforms import platform_bp
from blueprints.auth import auth_bp
from blueprints.family import family_bp
from blueprints.epic import epic_bp
from blueprints.gog import gog_bp
from blueprints.cubejoy import cubejoy_bp
from core.config import config, save_config
from core.cache import CACHE_DIR
from database import init_db
from epic_db import init_epic_db
from gog_db import init_gog_db
from cubejoy_db import init_cubejoy_db

# 确保缓存目录存在
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# 初始化数据库
init_db()
init_epic_db()
init_gog_db()
init_cubejoy_db()

app = Flask(__name__)
app.secret_key = 'steam_shelf_secret_key_change_me'
CORS(app)

# 注册所有蓝图
app.register_blueprint(games_bp)
app.register_blueprint(images_bp)
app.register_blueprint(platform_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(family_bp)
app.register_blueprint(epic_bp)
app.register_blueprint(gog_bp)
app.register_blueprint(cubejoy_bp)

APP_VERSION = "v1.0 Release"

@app.route('/api/version')
def get_version():
    return jsonify({"version": APP_VERSION})

# 主页
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # 确保配置项完整
    if 'epic_client_id' not in config:
        config['epic_client_id'] = ''
        save_config(config)
    if 'epic_client_secret' not in config:
        config['epic_client_secret'] = ''
        save_config(config)

    # 自动打开浏览器
    Timer(1, lambda: webbrowser.open('http://localhost:5000')).start()
    app.run(host='0.0.0.0', port=5000, debug=False)