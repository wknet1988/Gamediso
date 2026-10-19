// ==================== 应用入口 ====================
// ---- 模态框控制 ----
function showSettingsModal() {
    if (settingsModal) settingsModal.style.display = 'block';
    if (settingsMessage) settingsMessage.innerText = '';
    updateVersionDisplay();
}
function hideSettingsModal() { if (settingsModal) settingsModal.style.display = 'none'; }
function showSteamPathModal() { if (steamPathModal) steamPathModal.style.display = 'block'; }
function hideSteamPathModal() { if (steamPathModal) steamPathModal.style.display = 'none'; }

// ---- 版本号 ----
async function updateVersionDisplay() {
    try {
        const resp = await fetch('/api/version');
        const data = await resp.json();
        const verEl = document.getElementById('app-version');
        if (verEl) {
            const githubSvg = `<svg aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="16" height="16" fill="currentColor" style="display:inline-block; vertical-align:middle;"><path d="M10.226 17.284c-2.965-.36-5.054-2.493-5.054-5.256 0-1.123.404-2.336 1.078-3.144-.292-.741-.247-2.314.09-2.965.898-.112 2.111.36 2.83 1.01.853-.269 1.752-.404 2.853-.404 1.1 0 1.999.135 2.807.382.696-.629 1.932-1.1 2.83-.988.315.606.36 2.179.067 2.942.72.854 1.101 2 1.101 3.167 0 2.763-2.089 4.852-5.098 5.234.763.494 1.28 1.572 1.28 2.807v2.336c0 .674.561 1.056 1.235.786 4.066-1.55 7.255-5.615 7.255-10.646C23.5 6.188 18.334 1 11.978 1 5.62 1 .5 6.188.5 12.545c0 4.986 3.167 9.12 7.435 10.669.606.225 1.19-.18 1.19-.786V20.63a2.9 2.9 0 0 1-1.078.224c-1.483 0-2.359-.808-2.987-2.313-.247-.607-.517-.966-1.034-1.033-.27-.023-.359-.135-.359-.27 0-.27.45-.471.898-.471.652 0 1.213.404 1.797 1.235.45.651.921.943 1.483.943.561 0 .92-.202 1.437-.719.382-.381.674-.718.944-.943z"/></svg>`;
            verEl.innerHTML = `
                <div>${t.version_label} ${data.version}</div>
                <div><a href="https://github.com/wknet1988/Gamediso" target="_blank" style="color:#888 !important; text-decoration:none; font-size:13px;">${githubSvg} ${t.github_label}</a></div>
            `;
        }
        const year = new Date().getFullYear();
        const copyEl = document.getElementById('app-copyright');
        if (copyEl) {
            copyEl.innerText = `© ${year} Grandisoft`;
        }
    } catch(e) {
        console.error('获取版本失败', e);
    }
}

// ---- API 交互 ----
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

async function loadSteamgriddbApiKey() {
    try {
        const resp = await fetch('/api/status');
        const data = await resp.json();
        const key = data.steamgriddb_api_key || '';
        if (steamgriddbApiKeyInput) {
            steamgriddbApiKeyInput.value = key;
        }
    } catch(e) {}
}

// ---- 登录状态 ----
// 不再强制登录 Steam：直接进入主界面，按已配置的平台展示；
// 未配置任何平台时显示空状态引导用户前往授权管理。
async function checkStatus() {
    try {
        document.getElementById('app').style.display = 'flex';
        loadBackgroundFromStorage();
        loadSteamgriddbApiKey();
        await loadShelves();
    } catch (err) { console.error(err); }
}

// ---- 事件绑定 ----
document.getElementById('search-btn')?.addEventListener('click', onSearch);
document.getElementById('search-input')?.addEventListener('keypress', (e) => { if(e.key === 'Enter') onSearch(); });

// 空状态：引导前往授权管理
document.getElementById('empty-auth-btn')?.addEventListener('click', () => {
    document.getElementById('auth-btn')?.click();
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

// 赞助模态框
document.addEventListener('DOMContentLoaded', function() {
    const sponsorModal = document.getElementById('sponsor-modal');
    const sponsorBtn = document.getElementById('sponsor-btn');
    const closeSponsorBtn = document.querySelector('.close-sponsor-modal');

    if (sponsorBtn && sponsorModal) {
        sponsorBtn.addEventListener('click', () => {
            sponsorModal.style.display = 'block';
        });

        closeSponsorBtn?.addEventListener('click', () => {
            sponsorModal.style.display = 'none';
        });

        window.addEventListener('click', (e) => {
            if (e.target === sponsorModal) {
                sponsorModal.style.display = 'none';
            }
        });
    } else {
        console.warn('赞助按钮或模态框未找到');
    }
});

// ---- 启动 ----
applyI18n();
setTimeout(() => {
    ensureCounterElement();
    updateCounter();
}, 100);
checkStatus();

// 安装脚本（油猴）
const installScriptBtn = document.getElementById('install-script-btn');
if (installScriptBtn) {
    installScriptBtn.addEventListener('click', () => {
        window.open('/static/family_sync.user.js', '_blank');
        alert('脚本已下载，请打开 Tampermonkey 管理面板 → 实用程序 → 从文件安装，选择刚下载的文件。');
    });
}

// ==================== 同步进度管理（顶部条 + 持久化） ====================
let syncPollingInterval = null;
const SYNC_TASK_KEY = 'sync_task_id';

function showSyncProgress(taskId) {
    localStorage.setItem(SYNC_TASK_KEY, taskId);

    const container = document.getElementById('sync-progress-container');
    const fill = document.getElementById('sync-progress-fill');
    const text = document.getElementById('sync-progress-text');
    const percent = document.getElementById('sync-progress-percent');
    container.style.display = 'block';
    fill.style.width = '0%';
    text.innerText = t.sync_preparing;
    percent.innerText = '0%';

    if (syncPollingInterval) clearInterval(syncPollingInterval);

    syncPollingInterval = setInterval(async () => {
        try {
            const resp = await fetch(`/api/task/${taskId}`);
            const data = await resp.json();
            if (data.error) {
                clearInterval(syncPollingInterval);
                text.innerText = t.sync_error + data.error;
                percent.innerText = '';
                localStorage.removeItem(SYNC_TASK_KEY);
                return;
            }
            const progress = data.progress || 0;
            fill.style.width = progress + '%';
            percent.innerText = progress + '%';

            // 从 data.message 中提取数字（如 "已处理 51/123" 或 "Processed 51/123"）
            let displayText = '';
            if (data.message) {
                const match = data.message.match(/(\d+)\/(\d+)/);
                if (match) {
                    const processed = match[1];
                    const total = match[2];
                    displayText = t.sync_processing(processed, total);
                } else {
                    displayText = data.message;
                }
            }
            if (!displayText) {
                displayText = `进度 ${progress}%`;
            }
            text.innerText = displayText;

            if (data.done) {
                clearInterval(syncPollingInterval);
                localStorage.removeItem(SYNC_TASK_KEY);
                if (data.error) {
                    text.innerText = t.sync_failed(data.error);
                } else {
                    text.innerText = t.sync_complete;
                    // 同步完成后刷新侧边栏（新配置的平台会出现）并重载游戏列表
                    if (typeof loadShelves === 'function') {
                        loadShelves().then(() => {
                            if (typeof resetAndLoadGames === 'function') resetAndLoadGames();
                        });
                    } else if (typeof resetAndLoadGames === 'function') {
                        resetAndLoadGames();
                    }
                }
                setTimeout(() => {
                    container.style.display = 'none';
                }, 3000);
            }
        } catch (e) {
            console.error('轮询进度失败', e);
        }
    }, 1500);
}

// 页面加载时恢复进度（如果有未完成的任务）
function restoreSyncProgress() {
    const taskId = localStorage.getItem(SYNC_TASK_KEY);
    if (taskId) {
        // 检查任务是否仍在运行
        fetch(`/api/task/${taskId}`)
            .then(r => r.json())
            .then(data => {
                if (data.error || data.done) {
                    localStorage.removeItem(SYNC_TASK_KEY);
                    return;
                }
                showSyncProgress(taskId);
            })
            .catch(() => {});
    }
}

// ==================== 帮助模块 ====================
const helpModal = document.getElementById('help-modal');
const helpBtn = document.getElementById('help-btn');
const closeHelpBtn = document.querySelector('.close-help-modal');

function renderHelpContent() {
    const container = document.getElementById('help-content');
    if (!container) return;
    container.innerHTML = `
        <div style="margin-bottom: 16px;">
            <details>
                <summary style="cursor:pointer; font-weight:bold; font-size:16px; color:#66c0f4;">${t.help_q1}</summary>
                <p style="margin-top:10px; line-height:1.6;">${t.help_a1}</p>
            </details>
        </div>
        <div style="margin-bottom: 16px;">
            <details>
                <summary style="cursor:pointer; font-weight:bold; font-size:16px; color:#66c0f4;">${t.help_q2}</summary>
                <p style="margin-top:10px; line-height:1.6;">${t.help_a2}</p>
            </details>
        </div>
        <div style="margin-bottom: 16px;">
            <details>
                <summary style="cursor:pointer; font-weight:bold; font-size:16px; color:#66c0f4;">${t.help_q3}</summary>
                <p style="margin-top:10px; line-height:1.6;">${t.help_a3}</p>
            </details>
        </div>
        <div style="margin-bottom: 16px;">
            <details>
                <summary style="cursor:pointer; font-weight:bold; font-size:16px; color:#66c0f4;">${t.help_q4}</summary>
                <p style="margin-top:10px; line-height:1.6;">${t.help_a4}</p>
            </details>
        </div>
        <div style="margin-bottom: 16px;">
            <details>
                <summary style="cursor:pointer; font-weight:bold; font-size:16px; color:#66c0f4;">${t.help_q5}</summary>
                <p style="margin-top:10px; line-height:1.6;">${t.help_a5}</p>
            </details>
        </div>
    `;
}

helpBtn?.addEventListener('click', () => {
    renderHelpContent();
    helpModal.style.display = 'block';
});

closeHelpBtn?.addEventListener('click', () => {
    helpModal.style.display = 'none';
});

window.addEventListener('click', (e) => {
    if (e.target === helpModal) {
        helpModal.style.display = 'none';
    }
});

// 在页面初始化时调用
document.addEventListener('DOMContentLoaded', () => {
    restoreSyncProgress();
});

// ==================== 回到顶部按钮 ====================
const backToTopBtn = document.getElementById('back-to-top');

function handleBackToTopVisibility() {
    if (window.pageYOffset > 300) {
        backToTopBtn.style.display = 'block';
    } else {
        backToTopBtn.style.display = 'none';
    }
}

if (backToTopBtn) {
    window.addEventListener('scroll', handleBackToTopVisibility, { passive: true });
    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    // 初始检查一次
    setTimeout(handleBackToTopVisibility, 200);
}

// ---- 重置搜索 ----
document.getElementById('reset-search-btn')?.addEventListener('click', () => {
    const input = document.getElementById('search-input');
    if (input) {
        input.value = '';          // 清空输入框
        currentSearch = '';        // 重置搜索关键词
        resetAndLoadGames();       // 重新加载游戏列表
    }
});

// ==================== 横幅显示开关 ====================
const bannerToggle = document.getElementById('show-banner-toggle');
if (bannerToggle) {
    // 默认隐藏（false）
    const saved = localStorage.getItem('show_game_banner');
    bannerToggle.checked = saved !== null ? saved === 'true' : false;

    // 初始状态应用类
    if (bannerToggle.checked) {
        document.body.classList.add('show-banner');
    } else {
        document.body.classList.remove('show-banner');
    }

    bannerToggle.addEventListener('change', function() {
        localStorage.setItem('show_game_banner', this.checked ? 'true' : 'false');
        if (this.checked) {
            document.body.classList.add('show-banner');
        } else {
            document.body.classList.remove('show-banner');
        }
        // 重新加载游戏列表以更新横幅显示
        if (typeof resetAndLoadGames === 'function') {
            resetAndLoadGames();
        }
    });
}

// ---- 横幅风格选择 ----
const styleSelect = document.getElementById('banner-style-select');
if (styleSelect) {
    // 加载已保存的风格
    const savedStyle = localStorage.getItem('banner_style') || 'default';
    styleSelect.value = savedStyle;
    applyBannerStyle(savedStyle);

    styleSelect.addEventListener('change', function() {
        const style = this.value;
        localStorage.setItem('banner_style', style);
        applyBannerStyle(style);
    });
}

function applyBannerStyle(style) {
    // 移除所有已有的风格类
    document.body.classList.remove('banner-default', 'banner-playstation', 'banner-xbox', 'banner-nintendo', 'banner-gamesforwindows');
    // 添加对应类
    document.body.classList.add('banner-' + style);
}