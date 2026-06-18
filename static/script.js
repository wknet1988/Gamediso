// ==================== 国际化配置 ====================
const i18n = {
    zh: {
        app_name: '游戏藏经阁',
        shelf_header: '📀 游戏藏经阁',
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
        // 授权管理相关
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
        auth_cubejoy: '方块游戏',
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
        auth_epic_code_placeholder: '授权码'
    },
    en: {
        app_name: 'Gamepedia',
        shelf_header: '📀 Gamepedia',
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
        run: 'Run',
        loading_more: 'Loading more...',
        counter_text: '{loaded} of {total} games',
        epic_login: 'Login with Epic',
        epic_sync: '🔄 Sync Epic Games',
        epic_status: 'Epic status: ',
        not_logged_in: 'Not logged in',
        // Authorization related
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
        auth_epic_code_placeholder: 'Auth Code'
    }
};

let userLang = (navigator.language && navigator.language.startsWith('zh')) ? 'zh' : 'en';
const t = i18n[userLang];

function applyI18n() {
    document.title = t.app_name;
    const appNameEl = document.getElementById('app-name');
    if (appNameEl) appNameEl.innerText = t.app_name;
    // const shelfTitleEl = document.getElementById('shelf-title');
    // if (shelfTitleEl) shelfTitleEl.innerText = t.shelf_header;
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

// ==================== 全局变量 ====================
let currentPlatform = null;
let currentSearch = '';
let totalGames = 0;
let loadedCount = 0;
let isLoading = false;
let hasMore = true;
const PAGE_LIMIT = 28;

// DOM 引用
const settingsModal = document.getElementById('settings-modal');
const settingsApiKeyInput = document.getElementById('settings-api-key');
const saveApiKeyBtn = document.getElementById('save-api-key-settings');
const refreshLibraryBtn = document.getElementById('refresh-library-btn');
const settingsMessage = document.getElementById('settings-message');
const closeSettingsBtn = document.querySelector('.close-settings-modal');
const settingsBtn = document.getElementById('settings-btn');
const bgImageUpload = document.getElementById('bg-image-upload');
const clearBgBtn = document.getElementById('clear-bg-btn');
const steamPathModal = document.getElementById('steam-path-modal');
const steamPathInput = document.getElementById('modal-steam-path');
const saveSteamPathBtn = document.getElementById('modal-save-steam-path');
const pathError = document.getElementById('path-error');
const closePathModalBtn = document.querySelector('.close-path-modal');

// ==================== 辅助函数 ====================
function showLoadingMore(show) {
    const el = document.getElementById('loading-more');
    if (el) el.style.display = show ? 'block' : 'none';
}

function ensureCounterElement() {
    let counterEl = document.getElementById('game-counter');
    if (!counterEl) {
        counterEl = document.createElement('div');
        counterEl.id = 'game-counter';
        counterEl.className = 'dynamic-island';
        document.body.appendChild(counterEl);
    }
    // 强制设置内联样式，确保固定定位不被覆盖
    const style = counterEl.style;
    style.position = 'fixed';
    style.bottom = '20px';
    style.right = '20px';
    style.backgroundColor = 'rgba(0, 0, 0, 0.85)';
    style.backdropFilter = 'blur(10px)';
    style.color = 'white';
    style.padding = '6px 16px';
    style.borderRadius = '30px';
    style.fontSize = '14px';
    style.fontWeight = '500';
    style.zIndex = '99999';
    style.whiteSpace = 'nowrap';
    style.pointerEvents = 'none';
    style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';
    style.fontFamily = "system-ui, -apple-system, 'Segoe UI', sans-serif";
    return counterEl;
}

function updateCounter() {
    const counterEl = ensureCounterElement();
    const displayLoaded = Math.min(loadedCount, totalGames);
    const text = t.counter_text.replace('{loaded}', displayLoaded).replace('{total}', totalGames);
    counterEl.innerText = text;
}

function escapeHtml(str) {
    return str.replace(/[&<>]/g, m => {
        if (m === '&') return '&amp;';
        if (m === '<') return '&lt;';
        if (m === '>') return '&gt;';
        return m;
    });
}

function showLoading() {
    const ld = document.getElementById('loading');
    if (ld) ld.style.display = 'block';
}
function hideLoading() {
    const ld = document.getElementById('loading');
    if (ld) ld.style.display = 'none';
}

function loadBackgroundFromStorage() {
    const bgData = localStorage.getItem('custom_background');
    if (bgData) {
        document.body.style.backgroundImage = `url(${bgData})`;
        document.body.style.backgroundRepeat = 'repeat';
        document.body.style.backgroundSize = 'auto';
        document.body.classList.add('custom-bg');
    } else {
        document.body.style.backgroundImage = '';
        document.body.classList.remove('custom-bg');
    }
}

function saveBackgroundImage(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const imgData = e.target.result;
        localStorage.setItem('custom_background', imgData);
        document.body.style.backgroundImage = `url(${imgData})`;
        document.body.style.backgroundRepeat = 'repeat';
        document.body.classList.add('custom-bg');
        if (settingsMessage) settingsMessage.innerText = '背景图已更新';
    };
    reader.readAsDataURL(file);
}

function clearBackground() {
    localStorage.removeItem('custom_background');
    document.body.style.backgroundImage = '';
    document.body.classList.remove('custom-bg');
    if (settingsMessage) settingsMessage.innerText = '背景已移除';
}

async function updateVersionDisplay() {
    try {
        const resp = await fetch('/api/version');
        const data = await resp.json();
        const verEl = document.getElementById('app-version');
        if (verEl) {
            verEl.innerText = `版本: ${data.version}`;
        }
    } catch(e) {
        console.error('获取版本失败', e);
    }
}

function showSettingsModal() {
    if (settingsModal) settingsModal.style.display = 'block';
    if (settingsMessage) settingsMessage.innerText = '';
    updateVersionDisplay(); 
}
function hideSettingsModal() { if (settingsModal) settingsModal.style.display = 'none'; }
function showSteamPathModal() { if (steamPathModal) steamPathModal.style.display = 'block'; }
function hideSteamPathModal() { if (steamPathModal) steamPathModal.style.display = 'none'; }

// ==================== API 交互 ====================
async function saveApiKey() {
    const apiKey = settingsApiKeyInput.value.trim();
    if (!apiKey) { if (settingsMessage) settingsMessage.innerText = '请输入 API Key'; return; }
    saveApiKeyBtn.disabled = true;
    saveApiKeyBtn.innerText = '保存中...';
    try {
        const resp = await fetch('/api/set_api_key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        if (!resp.ok) throw new Error('保存失败');
        const initResp = await fetch('/api/init_library', { method: 'POST' });
        if (!initResp.ok) throw new Error('游戏库初始化失败');
        if (settingsMessage) settingsMessage.innerText = '✓ API Key 已保存，游戏库已更新';
        setTimeout(() => { hideSettingsModal(); window.location.reload(); }, 1500);
    } catch (err) {
        if (settingsMessage) settingsMessage.innerText = '错误：' + err.message;
    } finally {
        saveApiKeyBtn.disabled = false;
        saveApiKeyBtn.innerText = t.save_api_key;
    }
}

async function refreshLibrary() {
    if (!confirm('重新拉取游戏库会覆盖本地缓存，确定吗？')) return;
    refreshLibraryBtn.disabled = true;
    refreshLibraryBtn.innerText = '刷新中...';
    if (settingsMessage) settingsMessage.innerText = '正在从 Steam 下载游戏数据...';
    try {
        const resp = await fetch('/api/init_library', { method: 'POST' });
        if (!resp.ok) throw new Error('刷新失败');
        if (settingsMessage) settingsMessage.innerText = '✓ 游戏库已更新，页面即将刷新';
        setTimeout(() => window.location.reload(), 1500);
    } catch (err) {
        if (settingsMessage) settingsMessage.innerText = '错误：' + err.message;
    } finally {
        refreshLibraryBtn.disabled = false;
        refreshLibraryBtn.innerText = t.refresh_library;
    }
}

async function saveSteamPath() {
    const path = steamPathInput.value.trim();
    if (!path) { if (pathError) pathError.innerText = '请输入 Steam 安装路径'; return; }
    saveSteamPathBtn.disabled = true;
    try {
        const resp = await fetch('/api/set_steam_path', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ steam_path: path })
        });
        if (!resp.ok) {
            const err = await resp.json();
            throw new Error(err.error || '路径无效');
        }
        hideSteamPathModal();
        window.location.reload();
    } catch (err) {
        if (pathError) pathError.innerText = err.message;
    } finally {
        saveSteamPathBtn.disabled = false;
    }
}

// ==================== 游戏展示逻辑 ====================
function initLazyLoading() {
    const lazyImages = document.querySelectorAll('.lazy-img');
    if (lazyImages.length === 0) return;
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                const src = img.getAttribute('data-src');
                if (src) {
                    img.src = src;
                    img.removeAttribute('data-src');
                }
                observer.unobserve(img);
            }
        });
    }, { rootMargin: '200px' });
    lazyImages.forEach(img => observer.observe(img));
}

function appendGames(games) {
    const grid = document.getElementById('games-grid');
    if (!grid) return;
    if (games.length === 0 && loadedCount === 0) {
        grid.innerHTML = `<div style="text-align:center;padding:50px;">${t.no_games}</div>`;
        return;
    }

    let placeholderPath = '/static/steam_placeholder.png';
    if (currentPlatform.id === 'epic') {
        placeholderPath = '/static/epic_placeholder.png';
    } else if (currentPlatform.id === 'gog') {
        placeholderPath = '/static/gog_placeholder.png';
    } else if (currentPlatform.id === 'cubejoy') {
        placeholderPath = '/static/cubejoy_placeholder.png';
    }

    for (const game of games) {
        const card = document.createElement('div');
        card.className = 'game-card';

        // 商店链接
        let storeUrl = '';
        if (currentPlatform.id === 'steam') {
            storeUrl = `https://store.steampowered.com/app/${game.id}`;
        } else if (currentPlatform.id === 'epic') {
            const searchQuery = encodeURIComponent(game.name);
            storeUrl = `https://store.epicgames.com/browse?q=${searchQuery}`;
        } else if (currentPlatform.id === 'gog') {
            const searchQuery = encodeURIComponent(game.name);
            storeUrl = `https://www.gog.com/zh/games?query=${searchQuery}`;
        } else if (currentPlatform.id === 'cubejoy') {
            if (game.s_id) {
                storeUrl = `https://store.cubejoy.com/html/en/store/goodsdetail/detail${game.s_id}.html`;
            } else {
                storeUrl = "https://www.cubejoy.com/"; // 标记无效
            }
            runUrl = `asuka://runapp/?id=${game.id}`;
        }

        // 平台图标
        let iconUrl = '';
        if (currentPlatform.id === 'steam') {
            iconUrl = 'https://store.steampowered.com/favicon.ico';
        } else if (currentPlatform.id === 'epic') {
            iconUrl = 'https://www.epicgames.com/favicon.ico';
        } else if (currentPlatform.id === 'gog') {
            iconUrl = 'https://www.gog.com/favicon.ico';
        } else if (currentPlatform.id === 'cubejoy') {
            iconUrl = 'https://www.cubejoy.com/favicon.ico';
        }
        const iconHtml = iconUrl ? `<img src="${iconUrl}" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">` : '';

        // Steam 家庭库角标
        let badgeHtml = '';
        if (currentPlatform.id === 'steam' && game.type === 'shared') {
            badgeHtml = `<div style="position: absolute; top: 5px; right: 5px; background: rgba(0,0,0,0.7); color: #ffd700; font-size: 11px; padding: 2px 6px; border-radius: 20px; z-index: 10; backdrop-filter: blur(2px);">🏠 家庭库</div>`;
        }

        // 运行按钮（GOG 不显示）
        let actionsHtml = '';
        if (currentPlatform.id !== 'gog') {
            let runData = '';
            if (currentPlatform.id === 'cubejoy') {
                const runUrl = `asuka://runapp/?id=${game.id}`;
                    runData = `data-runurl="${runUrl}"`;
                } else {
                    console.warn('Cubejoy 游戏缺少 id:', game);
                }
            } else {
                runData = `data-id="${game.id}" data-platform="${currentPlatform.id}"`;
            }
            if (runData) {
                actionsHtml = `
                    <div class="actions">
                        <button class="run-btn" ${runData}>
                            ${iconHtml} ${t.run}
                        </button>
                    </div>
                `;
            }
        }

        // 图片元素，使用延迟重试的 onerror
        const imgSrc = game.image_url || '';
        const dataSrc = imgSrc;
        // 占位图（灰色 SVG）
        const placeholderSvg = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 200 100'%3E%3Crect width='200' height='100' fill='%232a3e55'/%3E%3Ctext x='50%25' y='50%25' dominant-baseline='middle' text-anchor='middle' fill='%2389a3b5'%3ELoading...%3C/text%3E%3C/svg%3E";

        // 内联 onerror 使用延迟重试
        const onerrorHandler = `
            if (!this.dataset.retry) {
                this.dataset.retry = '1';
                const self = this;
                setTimeout(function() {
                    self.src = self.dataset.src;
                }, 2000);
            } else {
                this.onerror = null;
                this.src = '${placeholderPath}';
            }
        `;

        card.innerHTML = `
            <div class="game-image-container" style="position: relative;">
                <a href="${storeUrl}" target="_blank" rel="noopener noreferrer" style="display: block;">
                    <img class="lazy-img" data-src="${dataSrc}" 
                         src="${placeholderSvg}" 
                         alt="${escapeHtml(game.name)}"
                         onerror="${onerrorHandler}">
                </a>
                ${badgeHtml}
            </div>
            <div class="game-name">${escapeHtml(game.name)}</div>
            ${actionsHtml}
        `;
        grid.appendChild(card);
    }

    // 绑定运行按钮事件
    document.querySelectorAll('.run-btn').forEach(btn => {
        btn.removeEventListener('click', runGameHandler);
        btn.addEventListener('click', runGameHandler);
    });

    // 初始化懒加载
    initLazyLoading();
}

function runGameHandler(e) {
    const btn = e.currentTarget;
    // 优先检查 data-runurl（Cubejoy）
    const runUrl = btn.dataset.runurl;
    if (runUrl) {
        window.location.href = runUrl;
        return;
    }
    // 原有逻辑（Steam / Epic）
    const id = btn.dataset.id;
    const platform = btn.dataset.platform;
    if (platform === 'steam') {
        window.location.href = `steam://run/${id}`;
    } else if (platform === 'epic') {
        window.location.href = `com.epicgames.launcher://apps/${id}?action=launch`;
    }
}

// 滚动加载
// ==================== 滚动加载（Firefox 兼容版） ====================
let scrollListenerAttached = false;
let scrollTimer = null;

function onScroll() {
    if (isLoading || !hasMore) return;
    if (scrollTimer) clearTimeout(scrollTimer);
    scrollTimer = setTimeout(() => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop || window.scrollY || 0;
        const windowHeight = window.innerHeight || document.documentElement.clientHeight || 0;
        const docHeight = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight,
            document.body.offsetHeight,
            document.documentElement.offsetHeight
        );
        if (scrollTop + windowHeight >= docHeight - 300) {
            loadMoreGames();
        }
        scrollTimer = null;
    }, 100);
}

function attachScrollListener() {
    if (scrollListenerAttached) return;
    window.addEventListener('scroll', onScroll, { passive: true });
    scrollListenerAttached = true;
    console.log('[attachScrollListener] 已绑定滚动监听');
}

function detachScrollListener() {
    if (!scrollListenerAttached) return;
    window.removeEventListener('scroll', onScroll, { passive: true });
    scrollListenerAttached = false;
}

// 新增：检查是否需要加载更多（针对 Firefox 内容高度不足的问题）
function checkAndLoadIfNeeded() {
    if (isLoading || !hasMore) return;
    // 延迟执行，确保 DOM 更新完成
    setTimeout(() => {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop || window.scrollY || 0;
        const windowHeight = window.innerHeight || document.documentElement.clientHeight || 0;
        const docHeight = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight,
            document.body.offsetHeight,
            document.documentElement.offsetHeight
        );
        // 如果内容高度小于视口高度，或者已经滚动到底部附近，则自动加载更多
        if (docHeight <= windowHeight || scrollTop + windowHeight >= docHeight - 300) {
            console.log('[checkAndLoadIfNeeded] 自动加载更多');
            loadMoreGames();
        }
    }, 200);
}

function resetAndLoadGames() {
    detachScrollListener();
    const grid = document.getElementById('games-grid');
    if (grid) grid.innerHTML = '';
    loadedCount = 0;
    hasMore = true;
    totalGames = 0;
    isLoading = false;
    updateCounter();
    attachScrollListener();
    loadMoreGames();
    // 初始加载后检查是否需要更多
    checkAndLoadIfNeeded();
}

async function loadMoreGames() {
    if (isLoading || !hasMore || !currentPlatform) {
        console.log('[loadMoreGames] 跳过加载:', { isLoading, hasMore, currentPlatform });
        return;
    }
    isLoading = true;
    showLoadingMore(true);

    const offset = loadedCount;
    let url = `/api/games?platform=${currentPlatform.id}&limit=${PAGE_LIMIT}&offset=${offset}`;
    if (currentSearch) url += `&search=${encodeURIComponent(currentSearch)}`;

    try {
        const resp = await fetch(url);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        const data = await resp.json();
        if (data.total !== undefined) totalGames = data.total;
        const newGames = data.games || [];

        const newLoadedCount = loadedCount + newGames.length;
        if (totalGames === 0 || newLoadedCount >= totalGames) {
            hasMore = false;
        } else {
            hasMore = true;
        }

        appendGames(newGames);
        loadedCount = newLoadedCount;
        updateCounter();
        // 更新标题
        let title = currentPlatform.name;
        if (currentSearch) title = `${t.search_result_prefix}${currentSearch}${t.search_result_suffix} - ${title}`;
        document.getElementById('current-shelf-title').innerText = title;

        // 强制触发 resize 事件，帮助 Firefox 重新计算布局
        window.dispatchEvent(new Event('resize'));

        // 加载完成后，检查是否还需要更多
        checkAndLoadIfNeeded();
    } catch (err) {
        console.error('[loadMoreGames] 加载失败', err);
        hasMore = false;
    } finally {
        isLoading = false;
        showLoadingMore(false);
        // 始终确保监听器绑定
        attachScrollListener();
    }
}

// 搜索
function onSearch() {
    const inp = document.getElementById('search-input');
    currentSearch = inp.value.trim();
    resetAndLoadGames();
}

// 动态侧边栏
async function loadShelves() {
    try {
        const resp = await fetch('/api/platforms');
        const platforms = await resp.json();
        const listEl = document.getElementById('shelf-list');
        listEl.innerHTML = '';
        for (const p of platforms) {
            const li = document.createElement('li');
            li.dataset.platform = p.id;

            let iconHtml = '';
            if (p.id === 'steam') {
                iconHtml = '<img src="https://store.steampowered.com/favicon.ico" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">';
            } else if (p.id === 'epic') {
                iconHtml = '<img src="https://www.epicgames.com/favicon.ico" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">';
            } else if (p.id === 'gog') {
                iconHtml = '<img src="https://www.gog.com/favicon.ico" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">';
            } else if (p.id === 'cubejoy') {
                iconHtml = '<img src="https://www.cubejoy.com/favicon.ico" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">';
                displayName = 'Cubejoy 方块';
            } else {
                iconHtml = p.icon || '📁';
            }

            li.innerHTML = `${iconHtml} ${p.name}`;

            if (currentPlatform && p.id === currentPlatform.id) li.classList.add('active');
            li.addEventListener('click', () => {
                if (currentPlatform && p.id === currentPlatform.id) return;
                currentPlatform = p;
                resetAndLoadGames();
                highlightActivePlatform();
            });
            listEl.appendChild(li);
        }
        if (!currentPlatform && platforms.length) {
            currentPlatform = platforms[0];
            resetAndLoadGames();
            highlightActivePlatform();
        }
    } catch (err) {
        console.error('加载平台列表失败', err);
    }
}

function highlightActivePlatform() {
    document.querySelectorAll('#shelf-list li').forEach(li => {
        if (li.dataset.platform === currentPlatform.id) li.classList.add('active');
        else li.classList.remove('active');
    });
}

// ==================== 登录状态检查 ====================
async function checkStatus() {
    try {
        const resp = await fetch('/api/status');
        const data = await resp.json();
        if (data.logged_in) {
            document.getElementById('login-panel').style.display = 'none';
            document.getElementById('app').style.display = 'flex';
            loadBackgroundFromStorage();
            loadShelves();
            resetAndLoadGames();
        } else {
            document.getElementById('login-panel').style.display = 'block';
            document.getElementById('app').style.display = 'none';
            if (data.need_api_key) showSettingsModal();
            else if (data.need_steam_path) showSteamPathModal();
        }
    } catch (err) { console.error(err); }
}

// ==================== 授权管理 ====================
const authModal = document.getElementById('auth-modal');
const authBtn = document.getElementById('auth-btn');
const closeAuthBtn = document.querySelector('.close-auth-modal');

authBtn?.addEventListener('click', () => {
    authModal.style.display = 'block';
    updateAuthStatus();
});

closeAuthBtn?.addEventListener('click', () => {
    authModal.style.display = 'none';
});
window.addEventListener('click', (e) => {
    if (e.target === authModal) authModal.style.display = 'none';
});

async function updateAuthStatus() {
    // Steam
    try {
        const resp = await fetch('/api/status');
        const data = await resp.json();
        const statusEl = document.getElementById('steam-status');
        if (data.logged_in) {
            statusEl.innerText = `✅ ${t.auth_logged_in} (${data.steamid})`;
            statusEl.style.color = '#6f6';
        } else {
            statusEl.innerText = `❌ ${t.auth_not_logged_in}`;
            statusEl.style.color = '#f66';
        }
    } catch(e) { console.error(e); }

    // Epic
    try {
        const resp = await fetch('/api/epic/status');
        const data = await resp.json();
        const statusEl = document.getElementById('epic-status');
        if (data.authenticated) {
            statusEl.innerText = `✅ ${t.auth_logged_in} (${data.account_name})`;
            statusEl.style.color = '#6f6';
        } else {
            statusEl.innerText = `❌ ${t.auth_not_logged_in}`;
            statusEl.style.color = '#f66';
        }
    } catch(e) { console.error(e); }

    // GOG
    try {
        const resp = await fetch('/api/gog/count');
        const data = await resp.json();
        const statusEl = document.getElementById('gog-status');
        if (data.count > 0) {
            statusEl.innerText = `✅ ${t.auth_sync} (${data.count} ${t.auth_gog_script})`;
            statusEl.style.color = '#6f6';
        } else {
            statusEl.innerText = `⏳ ${t.auth_gog_script}`;
            statusEl.style.color = '#ffa';
        }
    } catch(e) {
        console.error('GOG 状态检测失败', e);
        document.getElementById('gog-status').innerText = `❌ ${t.auth_not_logged_in}`;
        document.getElementById('gog-status').style.color = '#f66';
    }

    // Steam 家庭组
    try {
        const resp = await fetch('/api/family/count');
        const data = await resp.json();
        const statusEl = document.getElementById('family-status');
        if (data.count > 0) {
            statusEl.innerText = `✅ ${t.auth_family_sync} ${t.auth_family_count.replace('{count}', data.count)}`;
            statusEl.style.color = '#6f6';
        } else {
            statusEl.innerText = `⏳ ${t.auth_family_unsynced}`;
            statusEl.style.color = '#ffa';
        }
    } catch(e) {
        document.getElementById('family-status').innerText = `❌ ${t.auth_family_script}`;
        document.getElementById('family-status').style.color = '#aaa';
    }

    // Cubejoy
    try {
        const resp = await fetch('/api/cubejoy/count');
        const data = await resp.json();
        const statusEl = document.getElementById('cubejoy-status');
        if (data.count > 0) {
            statusEl.innerText = `✅ ${t.auth_sync} (${data.count} ${t.auth_cubejoy})`;
            statusEl.style.color = '#6f6';
        } else {
            statusEl.innerText = `⏳ ${t.auth_family_unsynced}`;
            statusEl.style.color = '#ffa';
        }
    } catch(e) {
        console.error('Cubejoy 状态检测失败', e);
        document.getElementById('cubejoy-status').innerText = `❌ ${t.auth_not_logged_in}`;
        document.getElementById('cubejoy-status').style.color = '#f66';
    }
}

// 授权管理按钮事件
document.getElementById('auth-steam-save-api')?.addEventListener('click', async () => {
    const apiKey = document.getElementById('auth-steam-api-key').value.trim();
    if (!apiKey) { alert('请输入 API Key'); return; }
    const resp = await fetch('/api/set_api_key', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: apiKey })
    });
    const data = await resp.json();
    if (data.success) {
        alert('API Key 保存成功！');
        updateAuthStatus();
    } else {
        alert('保存失败');
    }
});

// 授权管理：Steam 登录（新窗口打开）
document.getElementById('auth-steam-login')?.addEventListener('click', async () => {
    try {
        const resp = await fetch('/api/login');
        const data = await resp.json();
        if (data.login_url) {
            window.open(data.login_url, '_blank');
        } else {
            alert('无法获取登录链接');
        }
    } catch (err) {
        console.error('Steam 登录失败', err);
        alert('网络错误，请重试');
    }
});

document.getElementById('auth-steam-sync')?.addEventListener('click', async () => {
    const resp = await fetch('/api/init_library', { method: 'POST' });
    const data = await resp.json();
    if (data.success) {
        alert('Steam 游戏库同步成功！');
        updateAuthStatus();
    } else {
        alert('同步失败，请检查 API Key 或网络');
    }
});

document.getElementById('auth-family-install')?.addEventListener('click', () => {
    window.open('/static/family_sync.user.js', '_blank');
    alert('脚本已下载，请安装到 Tampermonkey 中，然后访问 Steam 商店页面点击右下角同步按钮。');
});

document.getElementById('auth-family-open')?.addEventListener('click', () => {
    window.open('https://store.steampowered.com/account/', '_blank');
    alert('请在 Steam 商店页面点击右下角的“同步到游戏藏经阁”按钮同步家庭库。');
});

document.getElementById('auth-epic-login')?.addEventListener('click', () => {
    window.open('https://legendary.gl/epiclogin', '_blank');
});

document.getElementById('auth-gog-store')?.addEventListener('click', () => {
    const lang = userLang === 'zh' ? 'zh' : 'en';
    window.open(`https://www.gog.com/${lang}/account/`, '_blank');
});

document.getElementById('auth-epic-submit')?.addEventListener('click', async () => {
    const code = document.getElementById('auth-epic-code').value.trim();
    if (!code) { alert('请输入授权码'); return; }
    const resp = await fetch('/api/epic/auth_code', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code })
    });
    const data = await resp.json();
    if (data.success) {
        alert(`Epic 认证成功！账号：${data.account_name}`);
        document.getElementById('auth-epic-code').value = '';
        updateAuthStatus();
        document.getElementById('auth-epic-sync').click();
    } else {
        alert('认证失败：' + (data.error || '未知错误'));
    }
});

document.getElementById('auth-epic-sync')?.addEventListener('click', async () => {
    const resp = await fetch('/api/epic/sync', { method: 'POST' });
    const data = await resp.json();
    if (data.success) {
        alert(`Epic 同步成功！共 ${data.count} 款游戏`);
        updateAuthStatus();
    } else {
        alert('同步失败：' + (data.error || '未知错误'));
    }
});

document.getElementById('auth-gog-install')?.addEventListener('click', () => {
    window.open('/static/gog_sync.user.js', '_blank');
    alert('脚本已下载，请安装到 Tampermonkey 中，然后访问 GOG 账户页面点击右下角同步。');
});

document.getElementById('auth-gog-open')?.addEventListener('click', () => {
    window.open('https://www.gog.com/account', '_blank');
});

document.getElementById('auth-gog-sync')?.addEventListener('click', () => {
    alert('请在 GOG 账户页面使用油猴脚本同步后，再点击此处刷新状态。');
    updateAuthStatus();
});

// Cubejoy
document.getElementById('auth-cubejoy-install')?.addEventListener('click', () => {
    window.open('/static/cubejoy_sync.user.js', '_blank');
    alert('脚本已下载，请安装到 Tampermonkey 中，然后访问方块游戏“我的游戏”页面点击右下角同步。');
});

document.getElementById('auth-cubejoy-store')?.addEventListener('click', () => {
    window.open('https://account.cubejoy.com/Comment/MyGame', '_blank');
});

// ==================== 事件绑定 ====================
document.getElementById('search-btn')?.addEventListener('click', onSearch);
document.getElementById('search-input')?.addEventListener('keypress', (e) => { if(e.key === 'Enter') onSearch(); });
document.getElementById('steam-login-btn')?.addEventListener('click', async () => {
    const resp = await fetch('/api/login');
    const data = await resp.json();
    window.location.href = data.login_url;
});
settingsBtn?.addEventListener('click', showSettingsModal);
saveApiKeyBtn?.addEventListener('click', saveApiKey);
refreshLibraryBtn?.addEventListener('click', refreshLibrary);
closeSettingsBtn?.addEventListener('click', hideSettingsModal);
saveSteamPathBtn?.addEventListener('click', saveSteamPath);
closePathModalBtn?.addEventListener('click', hideSteamPathModal);
bgImageUpload?.addEventListener('change', (e) => { if(e.target.files[0]) saveBackgroundImage(e.target.files[0]); });
clearBgBtn?.addEventListener('click', clearBackground);
window.addEventListener('click', (e) => {
    if (e.target === settingsModal) hideSettingsModal();
    if (e.target === steamPathModal) hideSteamPathModal();
});

// ==================== 回到顶部按钮 ====================
const backToTopBtn = document.getElementById('back-to-top');

function handleBackToTopVisibility() {
    if (window.pageYOffset > 300) {
        backToTopBtn.style.display = 'block';
        // 触发淡入（可选，已有 opacity 过渡）
    } else {
        backToTopBtn.style.display = 'none';
    }
}

if (backToTopBtn) {
    // 滚动时控制显示
    window.addEventListener('scroll', handleBackToTopVisibility, { passive: true });
    // 点击回到顶部
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    // 初始检查一次
    setTimeout(handleBackToTopVisibility, 200);
}

// 启动
applyI18n();
checkStatus();
// 确保计数器元素存在并应用样式
setTimeout(() => {
    ensureCounterElement();
    updateCounter();
}, 100);