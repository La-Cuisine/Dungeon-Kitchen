const COLS = 10, ROWS = 20, SZ = 30;
const board = document.getElementById('board');
const bctx = board.getContext('2d');
const ncanvas = document.getElementById('next-canvas');
const nctx = ncanvas.getContext('2d');

const COLORS = { I: '#5DCAA5', O: '#EF9F27', T: '#AFA9EC', S: '#1D9E75', Z: '#D85A30', J: '#378ADD', L: '#ED93B1' };
const SHAPES = {
    I: [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    O: [[1, 1], [1, 1]],
    T: [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
    S: [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
    Z: [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
    J: [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
    L: [[0, 0, 1], [1, 1, 1], [0, 0, 0]]
};
const TYPES = Object.keys(SHAPES);

// ─── SRS WALL KICK DATA ──────────────────────────────────────────────────────
// Tests de déplacement pour chaque transition de rotation (J, L, S, T, Z)
// Format : { "fromState>toState": [[dx,dy], ...] }
const WALL_KICKS = {
    // Pour J, L, S, T, Z
    "0>1": [[ 0,0],[-1,0],[-1,1],[ 0,-2],[-1,-2]],
    "1>0": [[ 0,0],[ 1,0],[ 1,-1],[ 0, 2],[ 1, 2]],
    "1>2": [[ 0,0],[ 1,0],[ 1,-1],[ 0, 2],[ 1, 2]],
    "2>1": [[ 0,0],[-1,0],[-1,1],[ 0,-2],[-1,-2]],
    "2>3": [[ 0,0],[ 1,0],[ 1,1],[ 0,-2],[ 1,-2]],
    "3>2": [[ 0,0],[-1,0],[-1,-1],[ 0, 2],[-1, 2]],
    "3>0": [[ 0,0],[-1,0],[-1,-1],[ 0, 2],[-1, 2]],
    "0>3": [[ 0,0],[ 1,0],[ 1, 1],[ 0,-2],[ 1,-2]],
};
// Wall kicks spéciaux pour la pièce I
const WALL_KICKS_I = {
    "0>1": [[ 0,0],[-2,0],[ 1,0],[-2,-1],[ 1, 2]],
    "1>0": [[ 0,0],[ 2,0],[-1,0],[ 2, 1],[-1,-2]],
    "1>2": [[ 0,0],[-1,0],[ 2,0],[-1, 2],[ 2,-1]],
    "2>1": [[ 0,0],[ 1,0],[-2,0],[ 1,-2],[-2, 1]],
    "2>3": [[ 0,0],[ 2,0],[-1,0],[ 2, 1],[-1,-2]],
    "3>2": [[ 0,0],[-2,0],[ 1,0],[-2,-1],[ 1, 2]],
    "3>0": [[ 0,0],[ 1,0],[-2,0],[ 1,-2],[-2, 1]],
    "0>3": [[ 0,0],[-1,0],[ 2,0],[-1, 2],[ 2,-1]],
};
// ────────────────────────────────────────────────────────────────────────────

let grid, current, next, score, lines, level, gameOver, paused;
let hiscore = parseInt(document.querySelector('#hi-score-val').textContent) || 0;
let dropTimer = null;
let particles2 = [];

// ─── ÉTAT MÉCANIQUE AVANCÉ ───────────────────────────────────────────────────
let lastActionWasTspin = false;    // dernière action = T-Spin ?
let lastActionWasTetris = false;   // dernière action = Tétris ?
let combo = 0;                     // compteur de combo (lignes consécutives)
let lastRotationWasKick = false;   // dernière rotation a utilisé un kick ?
let rotationState = 0;             // état de rotation 0-3
let lastRotationDir = null;        // direction de la dernière rotation
let actionLabel = '';              // texte d'action affiché
let actionTimer = null;            // timer pour effacer le label
// ────────────────────────────────────────────────────────────────────────────

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
// ────────────────────────────────────────────────────────────────────────────

// ─── SAUVEGARDE SCORE ────────────────────────────────────────────────────────
let scoreSaveTimeout = null;
function saveScore(scoreToSave) {
    if (scoreSaveTimeout) clearTimeout(scoreSaveTimeout);
    scoreSaveTimeout = setTimeout(() => {
        fetch("/save_score.php", {
            method: "POST", credentials: "include",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ score: scoreToSave, game_id: 1 })
        }).catch(() => {});
    }, 2000);
}
// ────────────────────────────────────────────────────────────────────────────

function newGrid() { return Array.from({ length: ROWS }, () => Array(COLS).fill(0)); }

function randomPiece() {
    const t = TYPES[Math.floor(Math.random() * TYPES.length)];
    const s = SHAPES[t].map(r => [...r]);
    return { type: t, color: COLORS[t], shape: s, x: Math.floor(COLS / 2) - Math.floor(s[0].length / 2), y: 0, rotState: 0 };
}

// ─── ROTATION SRS ────────────────────────────────────────────────────────────
function rotate(shape) {
    return shape[0].map((_, c) => shape.map(r => r[c]).reverse());
}

// Applique une rotation avec wall kicks SRS, retourne true si réussie
function tryRotate(piece, dir) {
    const newShape = dir > 0 ? rotate(piece.shape) : rotateBack(piece.shape);
    const fromState = piece.rotState;
    const toState = ((fromState + dir) + 4) % 4;
    const key = `${fromState}>${toState}`;
    const kicks = piece.type === 'I' ? WALL_KICKS_I[key] : WALL_KICKS[key];

    if (!kicks) return false; // pièce O, pas de kick

    for (const [dx, dy] of kicks) {
        // Note: dans SRS, dy positif = vers le bas sur la grille réelle
        // Nos coordonnées : y croît vers le bas, donc on inverse dy
        if (!collides(grid, piece, dx, -dy, newShape)) {
            piece.x += dx;
            piece.y -= dy;
            piece.shape = newShape;
            piece.rotState = toState;
            // Mémorise si c'est un kick (test index > 0)
            lastRotationWasKick = kicks.indexOf(kicks.find((k,i) => k[0]===dx && k[1]===dy)) > 0;
            lastRotationDir = dir;
            return true;
        }
    }
    return false;
}

function rotateBack(shape) {
    // Rotation inverse = 3 rotations normales
    let s = shape;
    s = rotate(s); s = rotate(s); s = rotate(s);
    return s;
}
// ────────────────────────────────────────────────────────────────────────────

function collides(g, piece, dx = 0, dy = 0, sh = null) {
    const s = sh || piece.shape;
    for (let r = 0; r < s.length; r++) for (let c = 0; c < s[r].length; c++) {
        if (!s[r][c]) continue;
        const nx = piece.x + c + dx, ny = piece.y + r + dy;
        if (nx < 0 || nx >= COLS || ny >= ROWS) return true;
        if (ny >= 0 && g[ny][nx]) return true;
    }
    return false;
}

function lock(g, piece) {
    piece.shape.forEach((r, ri) => r.forEach((v, ci) => {
        if (v) { const y = piece.y + ri, x = piece.x + ci; if (y >= 0) g[y][x] = piece.color; }
    }));
}

function clearLines(g) {
    let cleared = 0;
    for (let r = ROWS - 1; r >= 0; r--) {
        if (g[r].every(c => c)) { g.splice(r, 1); g.unshift(Array(COLS).fill(0)); cleared++; r++; }
    }
    return cleared;
}

// ─── DÉTECTION T-SPIN ────────────────────────────────────────────────────────
// Un T-Spin est détecté quand la pièce T se verrouille après une rotation
// et que 3 des 4 coins de la pièce T sont occupés (mur ou bloc)
function detectTSpin(g, piece) {
    if (piece.type !== 'T') return 'none';

    // Les 4 coins du carré 3x3 de la pièce T
    const corners = [
        [piece.y,     piece.x    ],
        [piece.y,     piece.x + 2],
        [piece.y + 2, piece.x    ],
        [piece.y + 2, piece.x + 2],
    ];

    let filledCorners = 0;
    let filledFront = 0;

    corners.forEach(([cy, cx]) => {
        if (cy < 0 || cy >= ROWS || cx < 0 || cx >= COLS || g[cy][cx]) filledCorners++;
    });

    // Les 2 coins "avant" (face pointée par la tête du T selon rotState)
    const frontCorners = getFrontCorners(piece);
    frontCorners.forEach(([cy, cx]) => {
        if (cy < 0 || cy >= ROWS || cx < 0 || cx >= COLS || g[cy][cx]) filledFront++;
    });

    if (filledCorners < 3) return 'none';

    // T-Spin Mini : seulement 1 coin avant rempli + kick utilisé
    if (filledFront < 2 && lastRotationWasKick) return 'mini';

    return 'full';
}

// Retourne les coordonnées des 2 coins "face" du T selon son état de rotation
function getFrontCorners(piece) {
    const x = piece.x, y = piece.y;
    switch (piece.rotState) {
        case 0: return [[y,   x], [y,   x+2]]; // face vers le haut
        case 1: return [[y,   x+2], [y+2, x+2]]; // face vers la droite
        case 2: return [[y+2, x], [y+2, x+2]]; // face vers le bas
        case 3: return [[y,   x], [y+2, x]]; // face vers la gauche
    }
    return [];
}
// ────────────────────────────────────────────────────────────────────────────

// ─── CALCUL DES POINTS ───────────────────────────────────────────────────────
function computeScore(cleared, tspin) {
    let pts = 0;
    let label = '';
    let isTspin = false;
    let isTetris = false;

    if (tspin === 'full') {
        isTspin = true;
        if (cleared === 0) { pts = 400;  label = 'T-SPIN'; }
        if (cleared === 1) { pts = 800;  label = 'T-SPIN SINGLE'; }
        if (cleared === 2) { pts = 1200; label = 'T-SPIN DOUBLE'; }
        if (cleared === 3) { pts = 1600; label = 'T-SPIN TRIPLE'; }
    } else if (tspin === 'mini') {
        isTspin = true;
        if (cleared === 0) { pts = 100; label = 'T-SPIN MINI'; }
        if (cleared === 1) { pts = 200; label = 'T-SPIN MINI SINGLE'; }
        if (cleared === 2) { pts = 400; label = 'T-SPIN MINI DOUBLE'; }
    } else {
        if (cleared === 1) { pts = 100;  label = 'SINGLE'; }
        if (cleared === 2) { pts = 300;  label = 'DOUBLE'; }
        if (cleared === 3) { pts = 500;  label = 'TRIPLE'; }
        if (cleared === 4) { pts = 800;  label = 'TETRIS'; isTetris = true; }
    }

    // Back-to-Back bonus (Tetris ou T-Spin enchaîné)
    let b2b = false;
    if (cleared > 0 && (isTspin || isTetris)) {
        if (lastActionWasTspin || lastActionWasTetris) {
            pts = Math.floor(pts * 1.5);
            label = 'BACK-TO-BACK\n' + label;
            b2b = true;
        }
        lastActionWasTspin = isTspin;
        lastActionWasTetris = isTetris;
    } else if (cleared > 0) {
        lastActionWasTspin = false;
        lastActionWasTetris = false;
    }

    // Combo bonus
    if (cleared > 0) {
        if (combo > 0) {
            pts += 50 * combo * level;
            label += combo > 1 ? `\nCOMBO x${combo + 1}` : '\nCOMBO';
        }
        combo++;
    } else {
        combo = 0;
    }

    return { pts: pts * level, label };
}
// ────────────────────────────────────────────────────────────────────────────

function drawCell(ctx, x, y, color, sz) {
    ctx.fillStyle = color;
    ctx.fillRect(x * sz + 1, y * sz + 1, sz - 2, sz - 2);
    ctx.fillStyle = 'rgba(255,255,255,0.15)';
    ctx.fillRect(x * sz + 1, y * sz + 1, sz - 2, 4);
    ctx.fillStyle = 'rgba(0,0,0,0.25)';
    ctx.fillRect(x * sz + 1, y * sz + sz - 5, sz - 2, 4);
}

function drawGhost() {
    let dy = 0;
    while (!collides(grid, current, 0, dy + 1)) dy++;
    if (dy === 0) return;
    current.shape.forEach((r, ri) => r.forEach((v, ci) => {
        if (v) {
            const gx = current.x + ci, gy = current.y + ri + dy;
            if (gy >= 0 && gy < ROWS) {
                bctx.fillStyle = 'rgba(187,221,221,0.12)';
                bctx.fillRect(gx * SZ + 1, gy * SZ + 1, SZ - 2, SZ - 2);
                bctx.strokeStyle = 'rgba(187,221,221,0.25)';
                bctx.lineWidth = 1;
                bctx.strokeRect(gx * SZ + 1, gy * SZ + 1, SZ - 2, SZ - 2);
            }
        }
    }));
}

// ─── AFFICHAGE ACTION LABEL ──────────────────────────────────────────────────
function showActionLabel(label) {
    if (!label) return;
    actionLabel = label;
    if (actionTimer) clearTimeout(actionTimer);
    actionTimer = setTimeout(() => { actionLabel = ''; render(); }, 2000);
}
// ────────────────────────────────────────────────────────────────────────────

function render() {
    bctx.fillStyle = '#04050f';
    bctx.fillRect(0, 0, board.width, board.height);
    bctx.strokeStyle = 'rgba(0,34,85,0.4)';
    bctx.lineWidth = 0.5;
    for (let r = 0; r < ROWS; r++) for (let c = 0; c < COLS; c++) {
        bctx.strokeRect(c * SZ, r * SZ, SZ, SZ);
        if (grid[r][c]) drawCell(bctx, c, r, grid[r][c], SZ);
    }
    if (current) {
        drawGhost();
        current.shape.forEach((r, ri) => r.forEach((v, ci) => { if (v) drawCell(bctx, current.x + ci, current.y + ri, current.color, SZ); }));
    }

    // Affichage du label d'action (T-Spin, Tetris, etc.)
    if (actionLabel) {
        const lines = actionLabel.split('\n');
        const cx = board.width / 2;
        bctx.textAlign = 'center';
        lines.forEach((line, i) => {
            const isFirst = i === 0;
            const isSub = i > 0;
            bctx.font = isFirst ? 'bold 15px monospace' : '11px monospace';
            bctx.fillStyle = isFirst ? '#AFA9EC' : '#5DCAA5';
            // Halo
            bctx.shadowColor = isFirst ? '#AFA9EC' : '#5DCAA5';
            bctx.shadowBlur = 12;
            bctx.fillText(line, cx, 40 + i * 20);
            bctx.shadowBlur = 0;
        });
    }

    if (gameOver) {
        bctx.fillStyle = 'rgba(4,5,15,0.78)';
        bctx.fillRect(0, board.height / 2 - 50, board.width, 100);
        bctx.fillStyle = '#BBDDDD'; bctx.font = '500 22px monospace'; bctx.textAlign = 'center';
        bctx.fillText('GAME OVER', board.width / 2, board.height / 2 - 10);
        bctx.font = '13px monospace'; bctx.fillStyle = '#6688aa';
        bctx.fillText('score : ' + score, board.width / 2, board.height / 2 + 18);
    }
    renderNext();
    renderHold();
}

function renderNext() {
    nctx.fillStyle = '#04050f'; nctx.fillRect(0, 0, 80, 80);
    if (!next) return;
    const sz = 16, s = next.shape, offX = Math.floor((5 - s[0].length) / 2), offY = Math.floor((5 - s.length) / 2);
    s.forEach((r, ri) => r.forEach((v, ci) => {
        if (v) { nctx.fillStyle = next.color; nctx.fillRect((offX + ci) * sz + 1, (offY + ri) * sz + 1, sz - 2, sz - 2); nctx.fillStyle = 'rgba(255,255,255,0.15)'; nctx.fillRect((offX + ci) * sz + 1, (offY + ri) * sz + 1, sz - 2, 4); }
    }));
}

function updateUI() {
    document.getElementById('score-val').textContent = score;
    document.getElementById('hi-score-val').textContent = hiscore;
    document.getElementById('level-val').textContent = level;
    document.getElementById('lines-val').textContent = lines;
    document.getElementById('level-bar').style.width = Math.min(100, (lines % 10) * 10) + '%';
}

function getDropInterval() { return Math.max(80, 500 - (level - 1) * 45); }
function stopTimer() { if (dropTimer !== null) { clearInterval(dropTimer); dropTimer = null; } }
function startTimer() { stopTimer(); dropTimer = setInterval(gameDrop, getDropInterval()); }

function spawnPiece() {
    current = next || randomPiece();
    next = randomPiece();
    // Réinitialise les états de rotation
    lastRotationWasKick = false;
    lastRotationDir = null;
    if (collides(grid, current)) {
        gameOver = true;
        render();
        stopTimer();
        stopKeepalive();
        if (scoreSaveTimeout) clearTimeout(scoreSaveTimeout);
        fetch("/save_score.php", {
            method: "POST", credentials: "include",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: new URLSearchParams({ score: hiscore, game_id: 1 })
        }).catch(() => {});
        return false;
    }
    return true;
}

function gameDrop() {
    if (!current || gameOver || paused) return;
    if (!collides(grid, current, 0, 1)) {
        current.y++;
        // Un mouvement vers le bas annule le flag de kick pour le T-Spin
        lastRotationWasKick = false;
    } else {
        // Verrouillage de la pièce
        const tspin = detectTSpin(grid, current);
        lock(grid, current);
        canHold = true;
        const cleared = clearLines(grid);

        if (cleared > 0 || tspin !== 'none') {
            const { pts, label } = computeScore(cleared, tspin);
            score += pts;
            if (score > hiscore) { hiscore = score; saveScore(hiscore); }
            lines += cleared;
            const newLevel = Math.floor(lines / 10) + 1;
            if (newLevel !== level) { level = newLevel; startTimer(); }
            if (label) showActionLabel(label);
            if (cleared > 0) triggerFlash(tspin !== 'none');
        } else {
            combo = 0; // Pas de ligne = combo brisé
        }

        updateUI();
        spawnPiece();
    }
    render();
}

function hardDrop() {
    if (!current || gameOver || paused) return;
    while (!collides(grid, current, 0, 1)) { current.y++; score += 2; }
    if (score > hiscore) { hiscore = score; saveScore(hiscore); }
    gameDrop();
}

function triggerFlash(isTspin = false) {
    const color = isTspin ? '#AFA9EC' : '#1D9E75';
    board.style.boxShadow = `0 0 18px ${color}`;
    setTimeout(() => board.style.boxShadow = '', 300);
    spawnParticles(isTspin);
}

let particles3 = [];
function spawnParticles(isTspin = false) {
    const colors = isTspin
        ? ['#AFA9EC', '#D8D3FF', '#7B72FF', '#C9C4FF']
        : ['#5DCAA5', '#EF9F27', '#AFA9EC', '#378ADD'];
    for (let i = 0; i < 24; i++) particles3.push({
        x: effc.width / 2, y: effc.height / 2,
        vx: (Math.random() - 0.5) * 6, vy: (Math.random() - 2) * 5,
        life: 1, color: colors[Math.floor(Math.random() * colors.length)]
    });
}

const effc = document.getElementById('effect');
const effctx = effc.getContext('2d');
function resizeEff() { effc.width = effc.parentElement.offsetWidth || 600; effc.height = effc.parentElement.offsetHeight || 640; }
window.addEventListener('resize', resizeEff);
setTimeout(resizeEff, 50);

(function animBg() {
    requestAnimationFrame(animBg);
    effctx.fillStyle = 'rgba(4,5,15,0.18)';
    effctx.fillRect(0, 0, effc.width, effc.height);
    particles3 = particles3.filter(p => p.life > 0.02);
    particles3.forEach(p => {
        p.x += p.vx; p.y += p.vy; p.vy += 0.15; p.life *= 0.91;
        effctx.globalAlpha = p.life; effctx.fillStyle = p.color;
        effctx.fillRect(p.x - 3, p.y - 3, 6, 6); effctx.globalAlpha = 1;
    });
})();

let holdPiece = null;
let canHold = true;

function holding() {
    if (!canHold) return;
    canHold = false;
    if (holdPiece === null) {
        holdPiece = { type: current.type, color: current.color, shape: SHAPES[current.type].map(r => [...r]), x: 0, y: 0, rotState: 0 };
        spawnPiece();
    } else {
        const tmp = holdPiece;
        holdPiece = { type: current.type, color: current.color, shape: SHAPES[current.type].map(r => [...r]), x: 0, y: 0, rotState: 0 };
        current = {
            type: tmp.type, color: tmp.color,
            shape: SHAPES[tmp.type].map(r => [...r]),
            x: Math.floor(COLS / 2) - Math.floor(SHAPES[tmp.type][0].length / 2),
            y: 0, rotState: 0
        };
    }
    render();
}

const hcanvas = document.getElementById('hold-canvas');
const hctx = hcanvas.getContext('2d');

function renderHold() {
    hctx.fillStyle = '#04050f';
    hctx.fillRect(0, 0, 80, 80);
    if (!holdPiece) return;
    const sz = 16, s = SHAPES[holdPiece.type];
    const offX = Math.floor((5 - s[0].length) / 2);
    const offY = Math.floor((5 - s.length) / 2);
    s.forEach((r, ri) => r.forEach((v, ci) => {
        if (v) {
            hctx.fillStyle = canHold ? holdPiece.color : '#444';
            hctx.fillRect((offX + ci) * sz + 1, (offY + ri) * sz + 1, sz - 2, sz - 2);
            hctx.fillStyle = 'rgba(255,255,255,0.15)';
            hctx.fillRect((offX + ci) * sz + 1, (offY + ri) * sz + 1, sz - 2, 4);
        }
    }));
}

function startGame() {
    grid = newGrid(); score = 0; lines = 0; level = 1; gameOver = false; paused = false;
    next = randomPiece();
    holdPiece = null; canHold = true;
    lastActionWasTspin = false; lastActionWasTetris = false;
    combo = 0; actionLabel = '';
    spawnPiece();
    startTimer();
    startKeepalive();
    updateUI(); render();
}

document.getElementById('start-btn').addEventListener('click', startGame);

document.addEventListener('keydown', e => {
    if (!current || gameOver) return;
    if (e.key === 'ArrowLeft' || e.key === 'q' || e.key === 'Q') {
        if (!collides(grid, current, -1, 0)) { current.x--; lastRotationWasKick = false; render(); }
    }
    else if (e.key === 'ArrowRight' || e.key === 'd' || e.key === 'D') {
        if (!collides(grid, current, 1, 0)) { current.x++; lastRotationWasKick = false; render(); }
    }
    else if (e.key === 'ArrowDown' || e.key === 's' || e.key === 'S') { gameDrop(); }
    else if (e.key === 'ArrowUp' || e.key === 'z' || e.key === 'Z') {
        // Rotation horaire avec SRS
        tryRotate(current, 1);
        render();
    }
    else if (e.key === 'x' || e.key === 'X') {
        // Rotation anti-horaire avec SRS
        tryRotate(current, -1);
        render();
    }
    else if (e.key === ' ') { e.preventDefault(); hardDrop(); }
    else if (e.key === 'p' || e.key === 'P') { paused = !paused; }
    else if (e.shiftKey) { holding(); }
});

startGame();