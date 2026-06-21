const board = document.getElementById('board');
const ctx = board.getContext('2d');

// --- Effets de fond ---
const effc = document.getElementById('effect');
const effctx = effc.getContext('2d');
let particles = [];

function resizeEff() { effc.width = window.innerWidth; effc.height = window.innerHeight; }
window.addEventListener('resize', resizeEff);
resizeEff();

//anime les particule
(function animBg() {
    requestAnimationFrame(animBg);
    effctx.fillStyle = 'rgba(4,5,15,0.25)';
    effctx.fillRect(0, 0, effc.width, effc.height);
    particles = particles.filter(p => p.life > 0.02);
    particles.forEach(p => {
        p.x += p.vx; p.y += p.vy; p.life *= 0.91;
        effctx.globalAlpha = p.life;
        effctx.fillStyle = p.color;
        effctx.fillRect(p.x - 2, p.y - 2, 4, 4);
        effctx.globalAlpha = 1;
    });
})();

function spawnParticles(bx, by, color) {
    const rect = board.getBoundingClientRect();
    const px = rect.left + bx * (rect.width / board.width);
    const py = rect.top + by * (rect.height / board.height);
    for (let i = 0; i < 16; i++) particles.push({
        x: px, y: py,
        vx: (Math.random() - 0.5) * 6,
        vy: (Math.random() - 0.5) * 6,
        life: 1, color
    });
}

// ─── KEEPALIVE ───────────────────────────────────────────────────────────────
let keepAliveInterval = null;

function startKeepalive() {
    stopKeepalive();
    keepAliveInterval = setInterval(() => {
        fetch('/keepalive.php', { method: 'POST', credentials: 'same-origin' })
            .then(r => r.json())
            .then(data => { if (!data.logged_in) stopKeepalive(); })
            .catch(() => {});
    }, 4 * 60 * 1000);
}

function stopKeepalive() {
    if (keepAliveInterval !== null) { clearInterval(keepAliveInterval); keepAliveInterval = null; }
}
// ─────────────────────────────────────────────────────────────────────────────

// --- Config difficulté ---
const DIFFICULTIES = {
    easy:   { cols: 9,  rows: 9,  mines: 10, sz: 28 },
    medium: { cols: 16, rows: 16, mines: 40, sz: 28 },
    hard:   { cols: 30, rows: 16, mines: 99, sz: 28 },
};

const NUM_COLORS = ['', '#378ADD', '#1D9E75', '#D85A30', '#002255', '#7B0000', '#1D9E75', '#000', '#555'];

let COLS, ROWS, MINES, SZ;
let grid, revealed, flagged;
let gameOver, won, firstClick, startTime, elapsed, timerInterval;
let currentDiff = 'medium';

// initialise bestTimes depuis les données PHP injectées (DB_HISCORES)
// si pas connecté ou pas de score, on met null
let bestTimes = {
    easy:   (typeof DB_HISCORES !== 'undefined' && DB_HISCORES.easy   > 0) ? DB_HISCORES.easy   : null,
    medium: (typeof DB_HISCORES !== 'undefined' && DB_HISCORES.medium > 0) ? DB_HISCORES.medium : null,
    hard:   (typeof DB_HISCORES !== 'undefined' && DB_HISCORES.hard   > 0) ? DB_HISCORES.hard   : null,
};

// Applique la config (colonnes, lignes, mines) selon la difficulté choisie
function setupDiff() {
    const d = DIFFICULTIES[currentDiff];
    COLS = d.cols; ROWS = d.rows; MINES = d.mines; SZ = d.sz;
    board.width  = COLS * SZ;
    board.height = ROWS * SZ;
}

// --- Grille ---
// Génère la grille avec mines et chiffres, safe autour du 1er clic
function buildGrid(safeX, safeY) {
    grid     = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
    revealed = Array.from({ length: ROWS }, () => Array(COLS).fill(false));
    flagged  = Array.from({ length: ROWS }, () => Array(COLS).fill(false));

    let placed = 0;
    while (placed < MINES) {
        const x = Math.floor(Math.random() * COLS);
        const y = Math.floor(Math.random() * ROWS);
        if (grid[y][x] === -1) continue;
        if (Math.abs(x - safeX) <= 1 && Math.abs(y - safeY) <= 1) continue;
        grid[y][x] = -1;
        placed++;
    }

    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
        if (grid[r][c] === -1) continue;
        let count = 0;
        for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) {
            const nr = r + dr, nc = c + dc;
            if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS && grid[nr][nc] === -1) count++;
        }
        grid[r][c] = count;
    }
}

// Révèle une case, se propage si case vide (flood fill)
function reveal(x, y) {
    if (x < 0 || x >= COLS || y < 0 || y >= ROWS) return;
    if (revealed[y][x] || flagged[y][x]) return;
    revealed[y][x] = true;
    if (grid[y][x] === 0) {
        for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) reveal(x + dc, y + dr);
    }
}

// Compte les drapeaux autour d'une case (pour le chord-click)
function countFlagged(x, y) {
    let count = 0;
    for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) {
        const nr = y + dr, nc = x + dc;
        if (nr >= 0 && nr < ROWS && nc >= 0 && nc < COLS && flagged[nr][nc]) count++;
    }
    return count;
}

// Vérifie si toutes les cases sans mine sont révélées
function checkWin() {
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
        if (grid[r][c] !== -1 && !revealed[r][c]) return false;
    }
    return true;
}

// Déclenche la victoire, sauvegarde le temps en DB
function triggerWin() {
    won = true;
    gameOver = true;
    clearInterval(timerInterval);
    stopKeepalive();

    // Met à jour le meilleur temps local si meilleur
    if (bestTimes[currentDiff] === null || elapsed < bestTimes[currentDiff]) {
        bestTimes[currentDiff] = elapsed;
    }

    // Envoi en BD
    fetch("save_score.php", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        credentials: "include",
        body: new URLSearchParams({
            score:      elapsed,
            game_id:    4,
            difficulty: currentDiff
        })
    });

    board.style.boxShadow = '0 0 24px #1D9E75';
    setTimeout(() => board.style.boxShadow = '', 800);
    render();
    updateUI();
}

// Déclenche la défaite, révèle toutes les mines
function triggerLoss(bx, by) {
    gameOver = true;
    clearInterval(timerInterval);
    stopKeepalive();
    board.classList.add('shake');
    setTimeout(() => board.classList.remove('shake'), 400);
    spawnParticles(bx * SZ + SZ / 2, by * SZ + SZ / 2, '#D85A30');
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
        if (grid[r][c] === -1) revealed[r][c] = true;
    }
    render();
}

// --- Rendu ---
// Dessine une case selon son état (cachée, drapeau, chiffre, mine)
function drawCell(c, r) {
    const px = c * SZ, py = r * SZ;
    const isRevealed = revealed[r][c];
    const isFlagged  = flagged[r][c];
    const isMine     = grid[r][c] === -1;

    if (!isRevealed) {
        ctx.fillStyle = '#0a1428';
        ctx.fillRect(px + 1, py + 1, SZ - 2, SZ - 2);
        ctx.fillStyle = 'rgba(187,221,221,0.07)';
        ctx.fillRect(px + 1, py + 1, SZ - 2, 3);

        if (isFlagged) {
            ctx.fillStyle = '#D85A30';
            ctx.fillRect(px + SZ / 2 - 1, py + 4, 2, SZ - 8);
            ctx.fillRect(px + SZ / 2 + 1, py + 4, SZ / 2 - 4, (SZ - 8) / 2);
            ctx.fillStyle = '#BBDDDD';
            ctx.fillRect(px + 2, py + SZ - 6, SZ - 4, 2);
        }
    } else {
        if (isMine) {
            ctx.fillStyle = gameOver && !won ? '#3a0a0a' : '#04050f';
            ctx.fillRect(px + 1, py + 1, SZ - 2, SZ - 2);
            const cx2 = px + SZ / 2, cy2 = py + SZ / 2, r2 = SZ / 2 - 4;
            ctx.fillStyle = '#D85A30';
            ctx.beginPath(); ctx.arc(cx2, cy2, r2, 0, Math.PI * 2); ctx.fill();
            ctx.strokeStyle = '#D85A30'; ctx.lineWidth = 1.5;
            for (let a = 0; a < 8; a++) {
                const angle = (a / 8) * Math.PI * 2;
                ctx.beginPath();
                ctx.moveTo(cx2 + Math.cos(angle) * (r2 + 1), cy2 + Math.sin(angle) * (r2 + 1));
                ctx.lineTo(cx2 + Math.cos(angle) * (r2 + 4), cy2 + Math.sin(angle) * (r2 + 4));
                ctx.stroke();
            }
        } else {
            ctx.fillStyle = '#04050f';
            ctx.fillRect(px + 1, py + 1, SZ - 2, SZ - 2);
            const num = grid[r][c];
            if (num > 0) {
                ctx.fillStyle = NUM_COLORS[num];
                ctx.font = `500 ${SZ - 8}px monospace`;
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(num, px + SZ / 2, py + SZ / 2 + 1);
            }
        }
    }
}

// Redessine toute la grille + écran game over
function render() {
    ctx.fillStyle = '#04050f';
    ctx.fillRect(0, 0, board.width, board.height);
    ctx.strokeStyle = 'rgba(0,34,85,0.5)';
    ctx.lineWidth = 0.5;
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
        ctx.strokeRect(c * SZ, r * SZ, SZ, SZ);
        drawCell(c, r);
    }

    if (gameOver) {
        const msg = won ? 'VICTOIRE !' : 'BOOM !';
        const col = won ? '#5DCAA5' : '#D85A30';
        ctx.fillStyle = 'rgba(4,5,15,0.82)';
        ctx.fillRect(0, board.height / 2 - 40, board.width, 80);
        ctx.fillStyle = col;
        ctx.font = '500 22px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(msg, board.width / 2, board.height / 2 - 8);
        ctx.font = '12px monospace';
        ctx.fillStyle = '#6688aa';
        ctx.fillText('START pour rejouer', board.width / 2, board.height / 2 + 16);
    }
}

// Met à jour mines restantes, temps, meilleur temps
function updateUI() {
    const flagCount = flagged.flat().filter(Boolean).length;
    document.getElementById('mines-val').textContent = MINES;
    document.getElementById('flags-val').textContent = MINES - flagCount;
    document.getElementById('time-val').textContent  = elapsed;

    const best = bestTimes[currentDiff];
    document.getElementById('hi-score-val').textContent = best !== null ? best + 's' : '--';
}

// --- Input ---
board.addEventListener('click', e => {
    if (gameOver) return;
    const rect   = board.getBoundingClientRect();
    const scaleX = board.width  / rect.width;
    const scaleY = board.height / rect.height;
    const c = Math.floor((e.clientX - rect.left) * scaleX / SZ);
    const r = Math.floor((e.clientY - rect.top)  * scaleY / SZ);
    if (c < 0 || c >= COLS || r < 0 || r >= ROWS) return;
    if (flagged[r][c]) return;

    if (firstClick) {
        firstClick = false;
        buildGrid(c, r);
        startTime = Date.now();
        startKeepalive();
        timerInterval = setInterval(() => {
            elapsed = Math.floor((Date.now() - startTime) / 1000);
            updateUI();
        }, 500);
    }

    if (revealed[r][c]) {
        if (countFlagged(c, r) === grid[r][c]) {
            for (let dr = -1; dr <= 1; dr++) for (let dc = -1; dc <= 1; dc++) {
                const nc2 = c + dc, nr2 = r + dr;
                if (nc2 >= 0 && nc2 < COLS && nr2 >= 0 && nr2 < ROWS && !flagged[nr2][nc2] && !revealed[nr2][nc2]) {
                    if (grid[nr2][nc2] === -1) { triggerLoss(nc2, nr2); return; }
                    reveal(nc2, nr2);
                }
            }
        }
    } else {
        if (grid[r][c] === -1) { triggerLoss(c, r); return; }
        reveal(c, r);
    }

    if (checkWin()) { triggerWin(); return; }
    updateUI();
    render();
});

board.addEventListener('contextmenu', e => {
    e.preventDefault();
    if (gameOver || firstClick) return;
    const rect   = board.getBoundingClientRect();
    const scaleX = board.width  / rect.width;
    const scaleY = board.height / rect.height;
    const c = Math.floor((e.clientX - rect.left) * scaleX / SZ);
    const r = Math.floor((e.clientY - rect.top)  * scaleY / SZ);
    if (c < 0 || c >= COLS || r < 0 || r >= ROWS) return;
    if (revealed[r][c]) return;
    flagged[r][c] = !flagged[r][c];
    updateUI();
    render();
});

document.getElementById('diff-select').addEventListener('change', e => {
    currentDiff = e.target.value;
    updateUI(); // met à jour le hiscore affiché immédiatement
});

// Réinitialise et lance une nouvelle partie
function startGame() {
    clearInterval(timerInterval);
    elapsed    = 0;
    firstClick = true;
    gameOver   = false;
    won        = false;
    setupDiff();
    grid     = Array.from({ length: ROWS }, () => Array(COLS).fill(0));
    revealed = Array.from({ length: ROWS }, () => Array(COLS).fill(false));
    flagged  = Array.from({ length: ROWS }, () => Array(COLS).fill(false));
    board.style.boxShadow = '';
    updateUI();
    render();
}

document.getElementById('start-btn').addEventListener('click', startGame);

startGame();