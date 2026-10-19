import os
import webbrowser
import webview
import threading
import time
import tkinter as tk
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

APP_VERSION = "v1.1 Release"

@app.route('/api/version')
def get_version():
    return jsonify({"version": APP_VERSION})

# 在系统默认浏览器中打开主界面（pywebview 窗口内点按钮时使用）
@app.route('/api/open_in_browser', methods=['POST'])
def open_in_browser():
    url = request.host_url.rstrip('/') + '/'
    try:
        ok = webbrowser.open(url)
        return jsonify({"success": bool(ok), "url": url})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

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
    # Timer(1, lambda: webbrowser.open('http://localhost:5000')).start()
    # app.run(host='0.0.0.0', port=5000, debug=False)
    
def start_flask():
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    # 在后台线程启动 Flask
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # 等待 Flask 启动
    for _ in range(30):
        try:
            import requests
            requests.get('http://localhost:5000', timeout=0.5)
            break
        except:
            time.sleep(0.1)
    else:
        print("警告：Flask 启动超时，但仍尝试打开窗口")

    # 获取屏幕尺寸（使用 tkinter）
    root = tk.Tk()
    root.withdraw()  # 隐藏 tkinter 主窗口
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.destroy()

    # 窗口尺寸设为屏幕尺寸的 95%，保留任务栏可见
    win_width = int(screen_width * 0.95)
    win_height = int(screen_height * 0.95)
    # 居中显示
    x = (screen_width - win_width) // 2
    y = (screen_height - win_height) // 2

    webview.create_window(
        'Gamediso',
        'http://localhost:5000',
        width=win_width,
        height=win_height,
        x=x,
        y=y,
        resizable=True,
        min_size=(800, 600),
        confirm_close=True
    )
    webview.start()