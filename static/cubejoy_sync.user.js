// ==UserScript==
// @name         Cubejoy 游戏库同步到游戏藏经阁
// @namespace    http://localhost:5000
// @version      1.6
// @description  从方块游戏平台同步游戏列表到本地游戏藏经阁
// @author       Gamepedia
// @match        https://account.cubejoy.com/Comment/MyGame
// @grant        GM_xmlhttpRequest
// @connect      localhost
// @connect      127.0.0.1
// @connect      account.cubejoy.com
// @connect      cubejoy.com
// ==/UserScript==

(function() {
    'use strict';

    const API_URL = 'http://localhost:5000/api/cubejoy/sync';
    const PAGE_SIZE = 24;
    const DELAY = 500;

    function addSyncButton() {
        const btn = document.createElement('button');
        btn.innerText = '🧊 同步到游戏藏经阁';
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

    function fetchPage(page) {
        return new Promise((resolve, reject) => {
            const url = `https://account.cubejoy.com/Comment/MyGameReq?pageIndex=${page}&pageSize=${PAGE_SIZE}`;
            console.log(`[Cubejoy] 请求第 ${page} 页: ${url}`);
            GM_xmlhttpRequest({
                method: 'POST',
                url: url,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'Accept': 'application/json, text/plain, */*',
                    'Origin': 'https://account.cubejoy.com',
                    'Referer': 'https://account.cubejoy.com/Comment/MyGame'
                },
                onload: function(resp) {
                    console.log(`[Cubejoy] 第 ${page} 页响应状态: ${resp.status}`);
                    const preview = resp.responseText.substring(0, 200);
                    console.log(`[Cubejoy] 响应预览: ${preview}`);
                    if (resp.status === 200) {
                        try {
                            const data = JSON.parse(resp.responseText);
                            console.log(`[Cubejoy] 第 ${page} 页数据条数: ${data.result?.list?.length || 0}`);
                            resolve(data);
                        } catch(e) {
                            console.error('[Cubejoy] JSON解析失败:', e);
                            reject(new Error(`解析JSON失败: ${e.message}\n响应预览: ${preview}`));
                        }
                    } else {
                        reject(new Error(`HTTP ${resp.status}: ${resp.statusText}\n响应预览: ${preview}`));
                    }
                },
                onerror: function(err) {
                    console.error('[Cubejoy] GM_xmlhttpRequest 错误:', err);
                    reject(new Error('网络请求失败'));
                }
            });
        });
    }

    async function fetchAllGames() {
        let page = 1;
        let allGames = [];
        let total = 0;
        do {
            const data = await fetchPage(page);
            if (data.resultCode !== 1) {
                throw new Error(`API 错误: ${data.msg}`);
            }
            const list = data.result.list || [];
            allGames = allGames.concat(list);
            total = data.result.total || 0;
            page++;
            if (page * PAGE_SIZE < total) {
                await new Promise(resolve => setTimeout(resolve, DELAY));
            }
        } while (page * PAGE_SIZE < total);
        return allGames;
    }

    const btn = addSyncButton();

    btn.onclick = async () => {
        btn.disabled = true;
        btn.innerText = '同步中...';
        try {
            const games = await fetchAllGames();
            if (!games.length) {
                alert('未获取到游戏，请确认已登录并访问“我的游戏”页面');
                return;
            }
            const formatted = games.map(g => ({
                game_id: String(g.appId),
                s_id: g.S_Id ? String(g.S_Id) : '',
                title: g.appName,
                image_url: g.D_Imgurl || ''
            }));
            GM_xmlhttpRequest({
                method: 'POST',
                url: API_URL,
                headers: { 'Content-Type': 'application/json' },
                data: JSON.stringify({ games: formatted }),
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
            console.error('[Cubejoy] 同步错误:', err);
        } finally {
            btn.disabled = false;
            btn.innerText = '🧊 同步到游戏藏经阁';
        }
    };
})();