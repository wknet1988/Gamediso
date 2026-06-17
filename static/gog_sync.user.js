// ==UserScript==
// @name         GOG 游戏库同步到游戏藏经阁
// @namespace    http://localhost:5000
// @version      2.0
// @description  从 GOG 账户页面抓取游戏列表并同步到本地游戏藏经阁
// @author       Gamepedia
// @match        https://www.gog.com/account*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// @connect      127.0.0.1
// ==/UserScript==

(function() {
    'use strict';

    const API_URL = 'http://localhost:5000/api/gog/sync_from_extension';

    function addSyncButton() {
        const btn = document.createElement('button');
        btn.innerText = '📀 同步到游戏藏经阁';
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

    const btn = addSyncButton();

    btn.onclick = async () => {
        btn.disabled = true;
        btn.innerText = '同步中...';
        try {
            const games = await fetchGogGames();
            if (!games.length) {
                alert('未找到游戏，请确保已登录 GOG 账号并访问“我的游戏”页面');
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
                            alert(`同步成功！共 ${data.count} 款游戏`);
                        } else {
                            alert('同步失败：' + (data.error || '未知错误'));
                        }
                    } catch(e) {
                        alert('同步失败：服务器返回无效响应');
                    }
                },
                onerror: function() {
                    alert('网络错误，请确保本地游戏藏经阁服务已启动 (http://localhost:5000)');
                }
            });
        } catch(err) {
            alert('抓取游戏失败：' + err.message);
        } finally {
            btn.disabled = false;
            btn.innerText = '📀 同步到游戏藏经阁';
        }
    };
})();