// ==================== 授权管理 ====================
const authModal = document.getElementById('auth-modal');
const authBtn = document.getElementById('auth-btn');
const closeAuthBtn = document.querySelector('.close-auth-modal');
const authMessage = document.getElementById('auth-message');

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

// ---------- 辅助函数 ----------
function setPill(el, state, text) {
    if (!el) return;
    el.innerText = text;
    el.classList.remove('pill-ok', 'pill-warn', 'pill-err');
    if (state) el.classList.add('pill-' + state);
}

function showAuthMessage(text, isError = false) {
    if (!authMessage) return;
    authMessage.innerText = text || '';
    authMessage.style.color = isError ? '#ff8a8a' : '#7ee08a';
}

// Epic 后端错误码 -> 界面文案
function epicErrorText(code, detail) {
    const map = {
        missing_credentials: t.err_missing_credentials,
        invalid_credentials: t.err_invalid_credentials,
        captcha_required: t.err_captcha_required,
        rate_limited: t.err_rate_limited,
        login_failed: t.err_login_failed,
        mfa_invalid: t.err_mfa_invalid,
        mfa_failed: t.err_mfa_failed,
        exchange_failed: t.err_exchange_failed,
        legendary_failed: t.err_legendary_failed,
        network_error: t.err_network,
        session_expired: t.err_session_expired,
        logout_failed: t.err_logout_failed,
    };
    let msg = map[code] || t.err_unknown;
    if (detail) msg += ` (${detail})`;
    return msg;
}

async function updateAuthStatus() {
    // ---- Steam 主号 ----
    try {
        const resp = await fetch('/api/status');
        const data = await resp.json();
        const el = document.getElementById('steam-status');
        if (data.logged_in) {
            setPill(el, 'ok', `✅ ${t.auth_logged_in} (${data.steamid})`);
        } else {
            setPill(el, 'err', `❌ ${t.auth_not_logged_in}`);
        }
    } catch (e) {
        console.error('Steam 主号状态获取失败', e);
        setPill(document.getElementById('steam-status'), 'err', '❌ 错误');
    }

    // ---- Steam 副号 ----
    try {
        const resp = await fetch('/api/alt/status');
        const data = await resp.json();
        const el = document.getElementById('steam-alt-status');
        if (data.logged_in) {
            setPill(el, 'ok', `✅ ${t.auth_logged_in} (${data.steamid})`);
        } else if (data.need_api_key) {
            setPill(el, 'warn', `⏳ ${t.auth_not_logged_in} (${t.auth_need_apikey})`);
        } else {
            setPill(el, 'err', `❌ ${t.auth_not_logged_in}`);
        }
    } catch (e) {
        console.error('Steam 副号状态获取失败', e);
        setPill(document.getElementById('steam-alt-status'), 'err', '❌ 错误');
    }

    // ---- Epic ----
    try {
        const resp = await fetch('/api/epic/status');
        const data = await resp.json();
        const el = document.getElementById('epic-status');
        if (data.authenticated) {
            setPill(el, 'ok', `✅ ${t.auth_logged_in}${data.account_name ? ` (${data.account_name})` : ''}`);
        } else {
            setPill(el, 'err', `❌ ${t.auth_not_logged_in}`);
        }
    } catch (e) {
        console.error('Epic 状态获取失败', e);
        setPill(document.getElementById('epic-status'), 'err', '❌ 错误');
    }

    // ---- SteamGridDB（可选，未配置不算错误） ----
    try {
        const resp = await fetch('/api/steamgriddb/status');
        const data = await resp.json();
        const statusEl = document.getElementById('steamgriddb-status');
        if (data.configured) {
            setPill(statusEl, 'ok', `✅ ${t.auth_configured}`);
        } else {
            setPill(statusEl, 'warn', `⏳ ${t.auth_not_configured}`);
        }
    } catch (e) {
        console.error('SteamGridDB 状态获取失败', e);
        setPill(document.getElementById('steamgriddb-status'), 'err', '❌ 错误');
    }

    // ---- GOG ----
    try {
        const resp = await fetch('/api/gog/count');
        const data = await resp.json();
        const el = document.getElementById('gog-status');
        if (data.count > 0) {
            setPill(el, 'ok', `✅ ${t.auth_synced_count.replace('{count}', data.count)}`);
        } else {
            setPill(el, 'warn', `⏳ ${t.auth_family_unsynced}`);
        }
    } catch (e) {
        console.error('GOG 状态获取失败', e);
        setPill(document.getElementById('gog-status'), 'err', '❌ 错误');
    }

    // ---- Steam 家庭组 ----
    try {
        const resp = await fetch('/api/family/count');
        const data = await resp.json();
        const el = document.getElementById('family-status');
        if (data.count > 0) {
            setPill(el, 'ok', `✅ ${t.auth_family_sync} ${t.auth_family_count.replace('{count}', data.count)}`);
        } else {
            setPill(el, 'warn', `⏳ ${t.auth_family_unsynced}`);
        }
    } catch (e) {
        console.error('家庭组状态获取失败', e);
        setPill(document.getElementById('family-status'), 'err', '❌ 错误');
    }

    // ---- Cubejoy ----
    try {
        const resp = await fetch('/api/cubejoy/count');
        const data = await resp.json();
        const el = document.getElementById('cubejoy-status');
        if (data.count > 0) {
            setPill(el, 'ok', `✅ ${t.auth_synced_count.replace('{count}', data.count)}`);
        } else {
            setPill(el, 'warn', `⏳ ${t.auth_family_unsynced}`);
        }
    } catch (e) {
        console.error('Cubejoy 状态获取失败', e);
        setPill(document.getElementById('cubejoy-status'), 'err', '❌ 错误');
    }
}

// ---------- Steam 主号 ----------
document.getElementById('auth-steam-save-api')?.addEventListener('click', async () => {
    const apiKey = document.getElementById('auth-steam-api-key').value.trim();
    if (!apiKey) { showAuthMessage(t.err_apikey_empty, true); return; }
    const btn = document.getElementById('auth-steam-save-api');
    btn.disabled = true;
    try {
        const resp = await fetch('/api/set_api_key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        const data = await resp.json();
        if (data.success) {
            showAuthMessage(t.auth_apikey_saved, false);
            updateAuthStatus();
            loadShelves();
        } else {
            showAuthMessage(t.auth_save_failed, true);
        }
    } catch (err) {
        showAuthMessage(t.err_network, true);
    } finally {
        btn.disabled = false;
    }
});

document.getElementById('auth-steam-login')?.addEventListener('click', async () => {
    try {
        const resp = await fetch('/api/login');
        const data = await resp.json();
        if (data.login_url) {
            window.open(data.login_url, '_blank');
            showAuthMessage(t.auth_steam_login_hint, false);
        } else {
            showAuthMessage(t.auth_login_url_failed, true);
        }
    } catch (err) {
        console.error('Steam 登录失败', err);
        showAuthMessage(t.err_network, true);
    }
});

document.getElementById('auth-steam-sync')?.addEventListener('click', async () => {
    localStorage.removeItem(SYNC_TASK_KEY);
    const resp = await fetch('/api/init_library', { method: 'POST' });
    const data = await resp.json();
    if (data.task_id) {
        showSyncProgress(data.task_id);
    } else if (data.success) {
        showAuthMessage(t.auth_sync_triggered, false);
        updateAuthStatus();
    } else {
        showAuthMessage(t.auth_sync_failed + (data.error || ''), true);
    }
});

// ---------- Steam 副号 ----------
document.getElementById('auth-steam-alt-login')?.addEventListener('click', async () => {
    try {
        const resp = await fetch('/api/alt/login');
        const data = await resp.json();
        if (data.login_url) {
            window.open(data.login_url, '_blank');
            showAuthMessage(t.auth_steam_login_hint, false);
        } else {
            showAuthMessage(t.auth_login_url_failed, true);
        }
    } catch (err) {
        console.error('Steam 副号登录失败', err);
        showAuthMessage(t.err_network, true);
    }
});

document.getElementById('auth-steam-alt-save-api')?.addEventListener('click', async () => {
    const apiKey = document.getElementById('auth-steam-alt-api-key').value.trim();
    if (!apiKey) { showAuthMessage(t.err_apikey_empty, true); return; }
    const btn = document.getElementById('auth-steam-alt-save-api');
    btn.disabled = true;
    try {
        const resp = await fetch('/api/alt/set_api_key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        const data = await resp.json();
        if (data.success) {
            showAuthMessage(t.auth_alt_apikey_saved, false);
            updateAuthStatus();
        } else {
            showAuthMessage(t.auth_save_failed, true);
        }
    } catch (err) {
        showAuthMessage(t.err_network, true);
    } finally {
        btn.disabled = false;
    }
});

document.getElementById('auth-steam-alt-sync')?.addEventListener('click', async () => {
    localStorage.removeItem(SYNC_TASK_KEY);
    const resp = await fetch('/api/alt/init_library', { method: 'POST' });
    const data = await resp.json();
    if (data.task_id) {
        showSyncProgress(data.task_id);
    } else if (data.success) {
        showAuthMessage(t.auth_sync_triggered, false);
        updateAuthStatus();
    } else {
        showAuthMessage(t.auth_sync_failed + (data.error || ''), true);
    }
});

// ---------- 家庭组 ----------
document.getElementById('auth-family-install')?.addEventListener('click', () => {
    window.open('/static/family_sync.user.js', '_blank');
    alert(t.auth_family_install_alert);
});

document.getElementById('auth-family-open')?.addEventListener('click', () => {
    window.open('https://store.steampowered.com/account/', '_blank');
    alert(t.auth_family_open_alert);
});

// ---------- Epic：页签切换 ----------
const epicTabPassword = document.getElementById('epic-tab-password');
const epicTabCode = document.getElementById('epic-tab-code');
const epicPanePassword = document.getElementById('epic-pane-password');
const epicPaneCode = document.getElementById('epic-pane-code');

function switchEpicTab(which) {
    if (!epicTabPassword || !epicTabCode) return;
    const usePassword = which === 'password';
    epicTabPassword.classList.toggle('active', usePassword);
    epicTabCode.classList.toggle('active', !usePassword);
    if (epicPanePassword) epicPanePassword.style.display = usePassword ? 'flex' : 'none';
    if (epicPaneCode) epicPaneCode.style.display = usePassword ? 'none' : 'flex';
    hideEpicMfa();
    showAuthMessage('');
}

epicTabPassword?.addEventListener('click', () => switchEpicTab('password'));
epicTabCode?.addEventListener('click', () => switchEpicTab('code'));

// ---------- Epic：账密登录 ----------
let epicMfaLoginId = null;

function hideEpicMfa() {
    const box = document.getElementById('epic-mfa-box');
    if (box) box.style.display = 'none';
    epicMfaLoginId = null;
}

function onEpicLoginSuccess(data) {
    hideEpicMfa();
    const pwd = document.getElementById('epic-login-password');
    if (pwd) pwd.value = '';
    showAuthMessage(`${t.epic_login_success}${data.account_name ? ` (${data.account_name})` : ''}`, false);
    updateAuthStatus();
    loadShelves();
    // 登录成功后自动同步游戏库
    document.getElementById('auth-epic-sync')?.click();
}

document.getElementById('epic-password-login-btn')?.addEventListener('click', async () => {
    const email = document.getElementById('epic-login-email').value.trim();
    const password = document.getElementById('epic-login-password').value;
    if (!email || !password) { showAuthMessage(t.err_missing_credentials, true); return; }
    const btn = document.getElementById('epic-password-login-btn');
    btn.disabled = true;
    btn.innerText = t.epic_logging_in;
    showAuthMessage('');
    try {
        const resp = await fetch('/api/epic/login_password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await resp.json();
        if (data.mfa_required) {
            epicMfaLoginId = data.login_id;
            const box = document.getElementById('epic-mfa-box');
            if (box) box.style.display = 'block';
            const codeInput = document.getElementById('epic-mfa-code');
            if (codeInput) { codeInput.value = ''; codeInput.focus(); }
            showAuthMessage('');
        } else if (data.success) {
            onEpicLoginSuccess(data);
        } else {
            showAuthMessage(epicErrorText(data.error, data.detail), true);
        }
    } catch (err) {
        console.error('Epic 账密登录异常', err);
        showAuthMessage(t.err_network, true);
    } finally {
        btn.disabled = false;
        btn.innerText = t.epic_login_btn;
    }
});

// 回车提交密码
document.getElementById('epic-login-password')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') document.getElementById('epic-password-login-btn')?.click();
});

document.getElementById('epic-mfa-verify')?.addEventListener('click', async () => {
    const code = document.getElementById('epic-mfa-code').value.trim();
    if (!code || !epicMfaLoginId) { showAuthMessage(t.err_mfa_empty, true); return; }
    const btn = document.getElementById('epic-mfa-verify');
    btn.disabled = true;
    btn.innerText = t.epic_mfa_verifying;
    showAuthMessage('');
    try {
        const resp = await fetch('/api/epic/login_mfa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ login_id: epicMfaLoginId, code })
        });
        const data = await resp.json();
        if (data.success) {
            onEpicLoginSuccess(data);
        } else if (data.error === 'mfa_invalid') {
            // 验证码错误：保留输入框，允许重试
            showAuthMessage(t.err_mfa_invalid, true);
        } else {
            showAuthMessage(epicErrorText(data.error, data.detail), true);
            hideEpicMfa();
        }
    } catch (err) {
        console.error('Epic 2FA 验证异常', err);
        showAuthMessage(t.err_network, true);
    } finally {
        btn.disabled = false;
        btn.innerText = t.epic_mfa_verify;
    }
});

document.getElementById('epic-mfa-cancel')?.addEventListener('click', async () => {
    const loginId = epicMfaLoginId;
    hideEpicMfa();
    if (loginId) {
        try {
            await fetch('/api/epic/login_cancel', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ login_id: loginId })
            });
        } catch (e) { /* 忽略 */ }
    }
    showAuthMessage('');
});

// ---------- Epic：授权码登录（备用方式） ----------
document.getElementById('auth-epic-login')?.addEventListener('click', () => {
    window.open('https://legendary.gl/epiclogin', '_blank');
    showAuthMessage(t.auth_epic_code_hint, false);
});

document.getElementById('auth-epic-submit')?.addEventListener('click', async () => {
    const code = document.getElementById('auth-epic-code').value.trim();
    if (!code) { showAuthMessage(t.err_code_empty, true); return; }
    const btn = document.getElementById('auth-epic-submit');
    btn.disabled = true;
    showAuthMessage('');
    try {
        const resp = await fetch('/api/epic/auth_code', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });
        const data = await resp.json();
        if (data.success) {
            document.getElementById('auth-epic-code').value = '';
            onEpicLoginSuccess(data);
        } else {
            showAuthMessage(t.auth_epic_auth_failed + (data.error || ''), true);
        }
    } catch (err) {
        showAuthMessage(t.err_network, true);
    } finally {
        btn.disabled = false;
    }
});

// ---------- Epic：同步 / 退出登录 ----------
document.getElementById('auth-epic-sync')?.addEventListener('click', async () => {
    localStorage.removeItem(SYNC_TASK_KEY);
    try {
        const resp = await fetch('/api/epic/sync', { method: 'POST' });
        const data = await resp.json();
        if (data.task_id) {
            showSyncProgress(data.task_id);
        } else if (data.success) {
            showAuthMessage(`${t.auth_epic_synced.replace('{count}', data.count)}`, false);
            updateAuthStatus();
            loadShelves();
        } else {
            showAuthMessage(t.auth_sync_failed + (data.error || ''), true);
        }
    } catch (err) {
        console.error('Epic 同步请求异常:', err);
        showAuthMessage(t.err_network, true);
    }
});

document.getElementById('auth-epic-logout')?.addEventListener('click', async () => {
    if (!confirm(t.epic_logout_confirm)) return;
    const btn = document.getElementById('auth-epic-logout');
    btn.disabled = true;
    try {
        const resp = await fetch('/api/epic/logout', { method: 'POST' });
        const data = await resp.json();
        if (data.success) {
            showAuthMessage(t.epic_logout_success, false);
            updateAuthStatus();
            loadShelves();
        } else {
            showAuthMessage(epicErrorText(data.error), true);
        }
    } catch (err) {
        showAuthMessage(t.err_network, true);
    } finally {
        btn.disabled = false;
    }
});

// ---------- GOG ----------
document.getElementById('auth-gog-install')?.addEventListener('click', () => {
    window.open('/static/gog_sync.user.js', '_blank');
    alert(t.auth_gog_install_alert);
});

document.getElementById('auth-gog-store')?.addEventListener('click', () => {
    const lang = userLang === 'zh' ? 'zh' : 'en';
    window.open(`https://www.gog.com/${lang}/account`, '_blank');
    alert(t.auth_gog_open_alert);
});

document.getElementById('auth-gog-sync')?.addEventListener('click', async () => {
    localStorage.removeItem(SYNC_TASK_KEY);
    const btn = document.getElementById('auth-gog-sync');
    btn.disabled = true;
    try {
        const resp = await fetch('/api/gog/sync', { method: 'POST' });
        const data = await resp.json();
        if (data.task_id) {
            showSyncProgress(data.task_id);
        } else if (data.success) {
            showAuthMessage(t.auth_epic_synced.replace('{count}', data.count), false);
            updateAuthStatus();
            loadShelves();
        } else {
            showAuthMessage(t.auth_sync_failed + (data.error || ''), true);
        }
    } catch (err) {
        showAuthMessage(t.err_network, true);
    } finally {
        btn.disabled = false;
    }
});

// ---------- Cubejoy ----------
document.getElementById('auth-cubejoy-install')?.addEventListener('click', () => {
    window.open('/static/cubejoy_sync.user.js', '_blank');
    alert(t.auth_cubejoy_install_alert);
});

document.getElementById('auth-cubejoy-store')?.addEventListener('click', () => {
    window.open('https://account.cubejoy.com/Comment/MyGame', '_blank');
    alert(t.auth_cubejoy_open_alert);
});

// ---------- SteamGridDB ----------
const steamgriddbApiKeyInput = document.getElementById('steamgriddb-api-key');
const saveSteamgriddbBtn = document.getElementById('save-steamgriddb-api-key');

saveSteamgriddbBtn?.addEventListener('click', async () => {
    const apiKey = steamgriddbApiKeyInput.value.trim();
    if (!apiKey) {
        showAuthMessage(t.steamgriddb_empty_error, true);
        return;
    }
    saveSteamgriddbBtn.disabled = true;
    try {
        const resp = await fetch('/api/set_steamgriddb_api_key', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ api_key: apiKey })
        });
        const data = await resp.json();
        if (data.success) {
            showAuthMessage(t.steamgriddb_saved, false);
            updateAuthStatus();
        } else {
            showAuthMessage(t.steamgriddb_save_failed + (data.error || ''), true);
        }
    } catch (err) {
        showAuthMessage(t.steamgriddb_network_error, true);
        console.error(err);
    } finally {
        saveSteamgriddbBtn.disabled = false;
    }
});
