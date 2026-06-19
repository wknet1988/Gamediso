// ==UserScript==
// @name         GOG Sync to Gamepedia
// @name-zh      GOG 同步到GP游戏收藏馆
// @namespace    http://localhost:5000
// @version      2.1
// @description  Fetch GOG library and sync to Gamepedia
// @description-zh  从 GOG 账户页面抓取游戏列表并同步到本地GP游戏收藏馆
// @author       Gamepedia
// @match        https://www.gog.com/account*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// @connect      127.0.0.1
// ==/UserScript==

(function() {
    'use strict';

    // ==================== 国际化配置 ====================
    const i18n = {
        zh: {
            sync_btn: '📀 同步到GP游戏收藏馆',
            sync_btn_syncing: '同步中...',
            no_games: '未获取到游戏，请确认已登录并访问“我的游戏”页面',
            sync_success: (count) => `同步成功！共 ${count} 款游戏`,
            sync_failed: (error) => `同步失败：${error || '未知错误'}`,
            network_error: '网络错误，请确保本地GP游戏收藏馆服务已启动 (http://localhost:5000)',
            fetch_failed: '抓取游戏失败：',
            invalid_response: '服务器返回无效响应'
        },
        en: {
            sync_btn: '📀 Sync to Gamepedia',
            sync_btn_syncing: 'Syncing...',
            no_games: 'No games found. Please ensure you are logged in and on the "My Games" page.',
            sync_success: (count) => `Sync successful! ${count} games`,
            sync_failed: (error) => `Sync failed: ${error || 'Unknown error'}`,
            network_error: 'Network error. Please ensure Gamepedia service is running (http://localhost:5000)',
            fetch_failed: 'Failed to fetch games: ',
            invalid_response: 'Invalid response from server'
        }
    };

    // 检测浏览器语言
    const userLang = (navigator.language && navigator.language.startsWith('zh')) ? 'zh' : 'en';
    const t = i18n[userLang];

    const API_URL = 'http://localhost:5000/api/gog/sync_from_extension';

    // ==================== 添加同步按钮 ====================
    function addSyncButton() {
        const btn = document.createElement('button');
        btn.innerText = t.sync_btn;
        btn.style.position = 'fixed';
        btn.style.bottom = '20px';
        btn.style.right = '20px';
        btn.style.zIndex = '9999';
        btn.style.padding = '8px 16px';
        btn.style.background = '#2c5a2e';
        btn.style.color = 'white';
        btn.style.border = 'none';
        btn.style.borderRadius = '30px';
        btn.style.cursor = 'pointer';
        btn.style.fontWeight = 'bold';
        btn.style.boxShadow = '0 2px 8px rgba(0,0,0,0.3)';
        btn.style.opacity = '0.8';
        btn.style.transition = 'opacity 0.2s';
        btn.onmouseenter = () => btn.style.opacity = '1';
        btn.onmouseleave = () => btn.style.opacity = '0.8';
        document.body.appendChild(btn);
        return btn;
    }

    // ==================== 抓取游戏数据 ====================
    async function fetchGogGames() {
        const allProducts = [];
        let page = 1;
        let totalPages = 1;

        try {
            do {
                const url = `https://www.gog.com/account/getFilteredProducts?mediaType=1&page=${page}&locale=en-US`;
                const response = await fetch(url, { credentials: 'include' });
                if (!response.ok) throw new Error(`HTTP ${response.status}`);
                const data = await response.json();
                if (data.products && data.products.length) {
                    allProducts.push(...data.products);
                }
                totalPages = data.totalPages || 1;
                page++;
            } while (page <= totalPages);
        } catch (e) {
            console.error('GOG 游戏抓取失败:', e);
            throw e;
        }

        // 转换为我们的格式
        return allProducts.map(p => ({
            game_id: p.id || p.slug,
            title: p.title,
            image_url: p.image || (p.cover ? p.cover : ''),
        }));
    }

    // ==================== 主逻辑 ====================
    const btn = addSyncButton();

    btn.onclick = async () => {
        btn.disabled = true;
        btn.innerText = t.sync_btn_syncing;
        try {
            const games = await fetchGogGames();
            if (!games.length) {
                alert(t.no_games);
                return;
            }
            GM_xmlhttpRequest({
                method: 'POST',
                url: API_URL,
                headers: { 'Content-Type': 'application/json' },
                data: JSON.stringify({ games }),
                onload: function(resp) {
                    try {
                        const data = JSON.parse(resp.responseText);
                        if (data.success) {
                            alert(t.sync_success(data.count));
                        } else {
                            alert(t.sync_failed(data.error));
                        }
                    } catch(e) {
                        alert(t.sync_failed(t.invalid_response));
                    }
                },
                onerror: function() {
                    alert(t.network_error);
                }
            });
        } catch(err) {
            alert(t.fetch_failed + err.message);
            console.error('[GOG Sync] 错误:', err);
        } finally {
            btn.disabled = false;
            btn.innerText = t.sync_btn;
        }
    };
})();