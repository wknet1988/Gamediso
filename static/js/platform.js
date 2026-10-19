// ==================== 侧边栏平台与搜索 ====================
function showEmptyState(show) {
    const emptyEl = document.getElementById('empty-state');
    const grid = document.getElementById('games-grid');
    const counter = document.getElementById('game-counter');
    const title = document.getElementById('current-shelf-title');
    if (emptyEl) emptyEl.style.display = show ? 'block' : 'none';
    if (grid) grid.style.display = show ? 'none' : 'grid';
    if (counter) counter.style.display = show ? 'none' : 'block';
    if (title) title.innerText = show ? '' : title.innerText;
    if (show && grid) grid.innerHTML = '';
}

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
            let displayName = p.name;

            if (p.id === 'steam') {
                iconHtml = '<img src="/static/images/steam.ico" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">';
            } else if (p.id === 'epic') {
                iconHtml = '<img src="/static/images/epic.ico" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">';
            } else if (p.id === 'gog') {
                iconHtml = '<img src="/static/images/gog.ico" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">';
            } else if (p.id === 'cubejoy') {
                iconHtml = '<img src="/static/images/cubejoy.ico" style="width:16px;height:16px;vertical-align:middle;margin-right:4px;">';
                displayName = userLang === 'zh' ? 'Cubejoy 方块' : 'Cubejoy';
            } else {
                iconHtml = p.icon || '📁';
            }

            li.innerHTML = `${iconHtml} ${displayName}`;

            if (currentPlatform && p.id === currentPlatform.id) li.classList.add('active');
            li.addEventListener('click', () => {
                if (currentPlatform && p.id === currentPlatform.id) return;
                currentPlatform = p;
                showEmptyState(false);
                resetAndLoadGames();
                highlightActivePlatform();
            });
            listEl.appendChild(li);
        }
        if (!currentPlatform && platforms.length) {
            currentPlatform = platforms[0];
            showEmptyState(false);
            resetAndLoadGames();
            highlightActivePlatform();
        } else if (!platforms.length) {
            // 未配置任何平台：显示空状态引导
            currentPlatform = null;
            showEmptyState(true);
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

function onSearch() {
    const inp = document.getElementById('search-input');
    currentSearch = inp.value.trim();
    resetAndLoadGames();
}