Gamepedia User Manual
[🇨🇳 点此查看中文说明](./README.zh.md)

Gamepedia is a multi-platform game library aggregator that helps you centrally view and manage games from Steam, Epic Games, GOG, and Cubejoy. Without switching multiple clients, you can browse all your games in a clean web interface, jump to store pages, launch games with one click, and enjoy locally cached cover images with infinite scrolling.
Features

    🔐 Unified Authorization – Configure API keys or authorization codes for each platform in one place.

    🕹️ Multi-platform Aggregation – Supports Steam (including Family Sharing), Epic Games, GOG, and Cubejoy. More platforms coming soon.

    🖼️ Smart Image Caching – Cover images are downloaded locally on first access, loading instantly afterwards, even offline (if cached).

    🔄 Infinite Scroll & Counter – Scroll without pagination; the counter in the bottom right shows loaded / total games.

    🚀 One-Click Launch – Click the "Run" button on any game card to launch via the respective platform’s official protocol (requires client installed).

    🏠 Steam Family Badge – Games shared via Steam Family show a "🏠 Family Library" badge on the top right corner.

    🔍 Game Search – Quickly filter games by name.

    🎨 Custom Background – Upload your own image as wallpaper (tiled mode).

    🌐 Internationalization – Automatically switches between Chinese and English based on browser language.

Installation & Running
Prerequisites

    Python 3.8 or higher

    Modern browser (Chrome / Firefox / Edge)

    (Optional) Tampermonkey or Violentmonkey extension for GOG and Cubejoy sync scripts.

Download & Launch

    ⚠️ Windows Users
    Double-click setup.bat for one-click installation. The script will automatically set up Python and install all dependencies.

    Clone or download this repository:
    bash

    git clone https://github.com/yourusername/gamepedia.git
    cd gamepedia

    Install dependencies:
    bash

    pip install -r requirements.txt

    If no requirements.txt, install manually:
    bash

    pip install flask flask-cors requests

    Start the application:
    bash

    python app.py

    Your browser will automatically open http://localhost:5000. Start using Gamepedia!

    After first start, go to "🔑 Authorization Management" to configure each platform (see below).

Platform Authorization & Sync Guide

Click the "🔑 Authorization Management" button in the sidebar, then follow these steps for each platform.
Platform	Authorization Method	Required Credentials	Sync Action
Steam	Web API Key + OpenID Login	1. Get Steam Web API Key (use localhost as domain)
2. Enter the API Key, click "Login" to complete OpenID auth	Click "Sync" to pull all owned games
Steam Family	Userscript	Install family_sync.user.js, visit Steam Store, click the bottom‑right button	Automatically syncs family‑shared games
Epic Games	OAuth Authorization Code	1. Click "Get Auth Code" to go to legendary.gl
2. Log in, copy the auth code
3. Paste and submit in the management panel	Click "Sync" to pull your Epic library
GOG	Userscript	Install gog_sync.user.js, visit GOG Account page, click the bottom‑right button	Automatically fetches all GOG games
Cubejoy	Userscript	Install cubejoy_sync.user.js, visit My Games, click the bottom‑right button	Automatically fetches all pages of your Cubejoy library

    Note: After installing the userscripts, ensure you are logged into the corresponding platform page and click the "Sync to Gamepedia" button.

Interface Walkthrough

    Sidebar: Shows all synced platform labels; click to switch game lists.

    Search Bar: Filter games in the current platform by name in real time.

    Game Card: Click the cover to open the store page (GOG opens a search page); click "Run" to launch the game.

    Counter (bottom right): Displays loaded / total games for the current platform.

    Back to Top: After scrolling beyond 300px, an "↑" button appears; click to smoothly scroll to the top.

    Settings: The "⚙️ Settings" button at the bottom of the sidebar allows custom background image upload.

Troubleshooting
Q: Game covers not showing or showing placeholder images?

A: Images are downloaded from the internet on first access. Check your network and be patient. If repeated failures occur, refresh the page (Ctrl+F5). Some games may lack cover images, so the platform‑specific placeholder will appear.
Q: Steam Family sync fails?

A: Ensure the userscript is installed and you are logged into the Steam Store. Click the sync button on the Store page. If still failing, reinstall the script or restart your browser.
Q: Epic auth code expired?

A: Auth codes are short‑lived (usually a few minutes). Submit quickly. If expired, just obtain a new one.
Q: After GOG or Cubejoy sync, no games appear?

A: Refresh the Gamepedia page (F5) after successful sync; the platform tab will appear. If still missing, check the corresponding database file (gog_games.db / cubejoy_games.db) for data.
Q: How to change language?

A: Language is auto‑detected from browser settings (Chinese/English). To force a specific language, modify the userLang variable in static/script.js or change your browser’s language preference.
Q: Cached images are corrupted?

A: The program includes automatic corruption detection and repair. When accessing the list, corrupted images will be re‑downloaded. You can also manually delete the platform sub‑folders under cache/ and restart the app.
Contributing & License

This project is released under the MIT License. Contributions and Pull Requests are welcome. When adding new platforms or improvements, please maintain modularity for easy integration.

Enjoy using Gamepedia – Happy Gaming!