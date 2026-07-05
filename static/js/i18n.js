// ==================== 国际化配置 ====================
const i18n = {
    zh: {
        app_name: 'Gamediso',
        shelf_header: '📀 Gamediso',
        login: '登录 Steam',
        settings: '⚙️ 设置',
        search: '🔍 搜索',
        search_placeholder: '搜索游戏名称...',
        settings_title: '⚙️ 设置',
        api_key_label: 'Steam Web API Key：',
        api_key_placeholder: '粘贴您的 API Key',
        api_key_link: '点击申请 API Key',
        save_api_key: '保存 API Key',
        refresh_library: '🔄 刷新游戏库',
        refresh_hint: '从 Steam 重新拉取所有游戏和封面',
        bg_label: '🎨 自定义背景图（平铺显示）：',
        clear_bg: '移除背景',
        bg_hint: '提示：上传的图片会以平铺方式作为背景。',
        steam_path_title: '请指定 Steam 安装路径',
        steam_path_desc: '为了读取您的游戏自定义列表，需要知道 Steam 安装目录。\n例如：D:\\Steam 或 C:\\Program Files (x86)\\Steam',
        steam_path_placeholder: 'Steam 安装路径',
        save_path: '保存路径',
        loading: '加载中...',
        no_games: '没有找到游戏',
        search_result_prefix: '搜索结果：“',
        search_result_suffix: '”',
        run: '运行',
        loading_more: '加载更多...',
        counter_text: '已加载 {loaded} / {total} 个游戏',
        epic_login: '登录 Epic 账号',
        epic_sync: '🔄 同步 Epic 游戏',
        epic_status: 'Epic 状态：',
        not_logged_in: '未登录',
        auth_management: '🔑 授权管理',
        auth_platform: '平台',
        auth_status: '状态',
        auth_action: '操作',
        auth_detecting: '检测中',
        auth_logged_in: '已登录',
        auth_not_logged_in: '未登录',
        auth_steam: 'Steam',
        auth_steam_family: 'Steam 家庭组',
        auth_epic: 'Epic Games',
        auth_gog: 'GOG',
        auth_cubejoy: 'Cubejoy 方块',
        auth_save: '保存',
        auth_login: '登录',
        auth_sync: '同步',
        auth_get_code: '获取授权码',
        auth_submit: '提交',
        auth_install_script: '安装脚本',
        auth_open_store: '打开游戏库',
        auth_family_script: '请使用油猴脚本同步',
        auth_family_sync: '已同步',
        auth_family_unsynced: '未同步',
        auth_family_count: '({count} 款共享)',
        auth_gog_script: '脚本同步',
        auth_epic_code_placeholder: '授权码',
        badge_family: '🏠 家庭库',
        badge_alt: '👤 副号',
        sponsor: '❤️ 赞助',
        sponsor_title: '☕ 赞助支持',
        sponsor_desc: '如果您觉得本项目有帮助，欢迎赞助以支持持续开发！',
        sponsor_thanks: '感谢您的支持！',
        version_label: '版本:',
        github_label: 'GitHub',
        alipay: '支付宝',
        wechat_pay: '微信支付',
        paypal: 'PayPal 贝宝',
        steam_alt: 'Steam 副号',
        sync_preparing: '准备中...',
        sync_processing: (processed, total) => `已同步 ${processed}/${total}`,
        sync_complete: '✅ 同步完成！',
        sync_failed: (error) => `❌ 同步失败: ${error}`,
        sync_error: '❌ 错误: ',
        steamgriddb_label: 'SteamGridDB API Key：',
        steamgriddb_placeholder: 'API Key',
        steamgriddb_save: '保存 API Key',
        steamgriddb_link: '点击注册并获取 API Key',
        steamgriddb_hint: '（免费，可为 Epic、GOG 带来高清封面图）',
        steamgriddb_saved: '✅ 保存成功！',
        steamgriddb_save_failed: '❌ 保存失败：',
        steamgriddb_network_error: '❌ 网络错误，请重试',
        steamgriddb_empty_error: '请输入 API Key',
        banner_label: '显示游戏卡片横幅',
        banner_hint: '在游戏卡片顶部显示平台标识',
        help: '❓ 帮助',
        help_title: '❓ 帮助中心',
        help_q1: '1. 如何在 Steam 授权并同步？',
        help_a1: `1. 在“授权管理”中找到 Steam 行。<br>
2. 点击“登录”按钮，在新窗口完成 Steam 账号授权（<strong>需已开启手机令牌</strong>）。<br>
3. 复制页面显示的 Steam Web API Key，粘贴到“API Key”输入框。<br>
4. 点击“保存”，然后点击“同步”即可拉取游戏库。<br>
<a href="https://steamcommunity.com/dev/apikey" target="_blank">点击这里申请 API Key</a>（需先登录 Steam）`,

help_q2: '2. 如何在 Epic 授权并同步？',
help_a2: `1. 在“授权管理”中找到 Epic 行。<br>
2. 点击“获取授权码”，新窗口打开 Epic 授权页面。<br>
3. 登录 Epic 账号后，页面会显示一个表格化的 JSON（类似键值对列表）。<br>
4. 找到表格中 authorizationCode 字段，其值类似 {"authorizationCode": "d887f29de1234b779067ce2b2fca3b84"}，复制该值。<br>
5. 将复制的授权码粘贴到输入框，点击“提交”。<br>
6. 认证成功后，点击“同步”即可拉取游戏库。<br><br>
<strong>SteamGridDB 高清封面图（可选）：</strong><br>
在授权管理中找到 SteamGridDB 行，输入从 <a href="https://www.steamgriddb.com/profile/preferences/api" target="_blank">SteamGridDB</a> 获取的 API Key 并保存。这会让 Epic 游戏使用更高清的封面图。`,

        help_q3: '3. 如何安装油猴脚本并使用同步功能？',
        help_a3: `1. 首先安装 Tampermonkey 浏览器扩展（Chrome / Firefox / Edge 均可）。<br>
2. 在“授权管理”中点击对应平台的“安装脚本”按钮（Steam 家庭组、GOG、方块游戏）。<br>
3. 下载 .user.js 文件后，打开 Tampermonkey 管理面板 → 实用程序 → 从文件安装，选择该文件。<br>
4. 安装后，在“授权管理”中点击“打开游戏库”进入对应平台页面。<br>
5. 页面右下角会出现“同步到Gamediso”按钮，点击即可同步游戏库。`,

        help_q4: '4. 软件是免费的吗？',
        help_a4: '软件完全开源且永久免费使用全部功能，如果您希望赞助本项目，请点击主界面“赞助”按钮。',
        help_q5: '5. 授权有安全风险吗？',
        help_a5: '本软件完全开源可审查，不含任何恶意代码。通过官方登录取得的认证信息都存储在本地，不会上传或分享给第三方。只要用户保持电脑环境可靠，则没有安全风险。但要谨防授权信息泄露，不使用时可在申请页面解授权，并删除config.db。',
    },
    en: {
        app_name: 'Gamediso',
        shelf_header: '📀 Gamediso',
        login: 'Login with Steam',
        settings: '⚙️ Settings',
        search: '🔍 Search',
        search_placeholder: 'Search game name...',
        settings_title: '⚙️ Settings',
        api_key_label: 'Steam Web API Key:',
        api_key_placeholder: 'Paste your API Key',
        api_key_link: 'Click here to get API Key',
        save_api_key: 'Save API Key',
        refresh_library: '🔄 Refresh Library',
        refresh_hint: 'Re-download all games and covers from Steam',
        bg_label: '🎨 Custom Background (tiled):',
        clear_bg: 'Remove Background',
        bg_hint: 'Upload an image to use as tiled background.',
        steam_path_title: 'Specify Steam Installation Path',
        steam_path_desc: 'To read your custom game lists, we need your Steam directory.\nE.g., D:\\Steam or C:\\Program Files (x86)\\Steam',
        steam_path_placeholder: 'Steam installation path',
        save_path: 'Save Path',
        loading: 'Loading...',
        no_games: 'No games found',
        search_result_prefix: 'Search results: “',
        search_result_suffix: '”',
        run: 'Play',
        loading_more: 'Loading more...',
        counter_text: '{loaded} of {total} games',
        epic_login: 'Login with Epic',
        epic_sync: '🔄 Sync Epic Games',
        epic_status: 'Epic status: ',
        not_logged_in: 'Not logged in',
        auth_management: '🔑 Auth Manager',
        auth_platform: 'Platform',
        auth_status: 'Status',
        auth_action: 'Action',
        auth_detecting: 'Detecting...',
        auth_logged_in: 'Logged in',
        auth_not_logged_in: 'Not logged in',
        auth_steam: 'Steam',
        auth_steam_family: 'Steam Family',
        auth_epic: 'Epic Games',
        auth_gog: 'GOG',
        auth_cubejoy: 'Cubejoy',
        auth_save: 'Save',
        auth_login: 'Login',
        auth_sync: 'Sync',
        auth_get_code: 'Get Auth Code',
        auth_submit: 'Submit',
        auth_install_script: 'Install Script',
        auth_open_store: 'Open Library',
        auth_family_script: 'Please use userscript to sync',
        auth_family_sync: 'Synced',
        auth_family_unsynced: 'Not synced',
        auth_family_count: '({count} shared)',
        auth_gog_script: 'Script Sync',
        auth_epic_code_placeholder: 'Auth Code',
        badge_family: '🏠 Family',
        badge_alt: '👤 Alt',
        sponsor: '❤️ Sponsor',
        sponsor_title: '☕ Sponsor Support',
        sponsor_desc: 'If you find this project helpful, welcome to sponsor to support continued development!',
        sponsor_thanks: 'Thank you for your support!',
        version_label: 'Version:',
        github_label: 'GitHub',
        alipay: 'Alipay',
        wechat_pay: 'WeChat Pay',
        paypal: 'PayPal',
        steam_alt: 'Steam (alt)',
        sync_preparing: 'Preparing...',
        sync_processing: (processed, total) => `Processed ${processed}/${total}`,
        sync_complete: '✅ Sync complete!',
        sync_failed: (error) => `❌ Sync failed: ${error}`,
        sync_error: '❌ Error: ',
        steamgriddb_label: 'SteamGridDB API Key:',
        steamgriddb_placeholder: 'API Key',
        steamgriddb_save: 'Save API Key',
        steamgriddb_link: 'Click here to register and get API Key',
        steamgriddb_hint: '(Free, brings high-quality covers for Epic & GOG)',
        steamgriddb_saved: '✅ Saved successfully!',
        steamgriddb_save_failed: '❌ Save failed: ',
        steamgriddb_network_error: '❌ Network error, please retry',
        steamgriddb_empty_error: 'Please enter API Key',
        banner_label: 'Show Game Card Banner',
        banner_hint: 'Display platform badge on game card top',
        help: '❓ Help',
        help_title: '❓ Help Center',
        help_q1: '1. How to authorize and sync Steam?',
        help_a1: `1. Find the Steam row in "Authorization Management".<br>
2. Click "Login" and complete Steam account authorization in the new window (<strong>Mobile Authenticator must be enabled</strong>).<br>
3. Copy the Steam Web API Key shown on the page and paste it into the "API Key" field.<br>
4. Click "Save", then click "Sync" to pull your game library.<br>
<a href="https://steamcommunity.com/dev/apikey" target="_blank">Click here to get API Key</a> (login required)`,

help_q2: '2. How to authorize and sync Epic?',
help_a2: `1. Find the Epic row in "Authorization Management".<br>
2. Click "Get Auth Code" to open the Epic authorization page.<br>
3. After logging in, the page will display a table-formatted JSON (like a key-value list).<br>
4. Locate the authorizationCode field, which looks like {"authorizationCode": "d887f29de1234b779067ce2b2fca3b84"}, and copy it.<br>
5. Paste the code into the input field and click "Submit".<br>
6. After authentication, click "Sync" to pull your Epic library.<br><br>
<strong>SteamGridDB HD Covers (Optional):</strong><br>
Find the SteamGridDB row in "Authorization Management", enter the API Key obtained from <a href="https://www.steamgriddb.com/profile/preferences/api" target="_blank">SteamGridDB</a> and save it. This will provide higher-quality covers for Epic games.`,

        help_q3: '3. How to install userscripts and use sync?',
        help_a3: `1. Install Tampermonkey extension (Chrome / Firefox / Edge).<br>
2. In "Authorization Management", click "Install Script" for the platform (Steam Family, GOG, Cubejoy).<br>
3. After downloading the .user.js file, open Tampermonkey dashboard → Utilities → Install from file, and select it.<br>
4. After installation, click "Open Library" in "Authorization Management" to visit the platform page.<br>
5. A "Sync to Gamediso" button will appear at the bottom right; click it to sync.`,

        help_q4: '4. Is the software free?',
        help_a4: 'The software is completely open-source and permanently free to use all features. If you wish to sponsor this project, please click the "Sponsor" button on the main interface.',
        help_q5: '5. Are there security risks with authorization?',
        help_a5: 'This software is completely open source and verifiable, containing no malicious code. All authentication information obtained through official login is stored locally and will not be uploaded or shared with third parties. As long as users keep their computer environment secure, there is no security risk. However, be cautious about authorization information leakage, and when not in use, you can revoke authorization on the application page，and delete the config.db file.',    }
};

let userLang = (navigator.language && navigator.language.startsWith('zh')) ? 'zh' : 'en';
const t = i18n[userLang];

function applyI18n() {
    document.title = t.app_name;
    const appNameEl = document.getElementById('app-name');
    if (appNameEl) appNameEl.innerText = t.app_name;
    const shelfTitleEl = document.getElementById('shelf-title');
    if (shelfTitleEl) shelfTitleEl.innerText = t.shelf_header;
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (t[key]) el.innerText = t[key];
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
        const key = el.getAttribute('data-i18n-placeholder');
        if (t[key]) el.placeholder = t[key];
    });
    const loadingEl = document.getElementById('loading');
    if (loadingEl && t.loading) loadingEl.innerText = t.loading;
}