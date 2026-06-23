const COLS = 20, ROWS = 20, SZ = 20;
const W = COLS * SZ, H = ROWS * SZ;

const board = document.getElementById('board');
board.width = W;
board.height = H;
const ctx = board.getContext('2d');

// --- Effets de fond ---
const effc = document.getElementById('effect');
const effctx = effc.getContext('2d');
let particles = [];

// Redimensionne le canvas d'effets à la taille de la fenêtre
function resizeEff() {
    effc.width = window.innerWidth;
    effc.height = window.innerHeight;
}
window.addEventListener('resize', resizeEff);
resizeEff();

// anime les particules
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

// Génère des particules à une position du board
function spawnParticles(bx, by, color) {
    const rect = board.getBoundingClientRect();
    const px = rect.left + bx * (rect.width / W);
    const py = rect.top + by * (rect.height / H);
    for (let i = 0; i < 16; i++) {
        particles.push({
            x: px, y: py,
            vx: (Math.random() - 0.5) * 5,
            vy: (Math.random() - 0.5) * 5,
            life: 1,
            color
        });
    }
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

// --- État ---
let snake, dir, nextDir, food, bonus;
let score, level, gameOver, paused;
let hiscore = parseInt(document.querySelector('#hi-score-val').textContent) || 0;
let stepTimer = null;
let eaten = 0; // pour le niveau

const LEVEL_THRESHOLD = 5; // pommes par niveau

// Calcule la vitesse du serpent selon le niveau
function getInterval() { return Math.max(60, 220 - (level - 1) * 18); }

// Génère une position aléatoire libre sur la grille
function randomCell(exclude = []) {
    let cell;
    do {
        cell = { x: Math.floor(Math.random() * COLS), y: Math.floor(Math.random() * ROWS) };
    } while (exclude.some(e => e.x === cell.x && e.y === cell.y));
    return cell;
}

// Place la nourriture (et un bonus éventuel) aléatoirement
function placeFood() {
    food = randomCell(snake);
    // bonus : pomme spéciale toutes les 5 pommes mangées
    bonus = null;
    if (eaten > 0 && eaten % 5 === 0) {
        bonus = { ...randomCell([...snake, food]), timer: 80 };
    }
}

// Initialise toutes les variables pour une nouvelle partie
function initGame() {
    const cx = Math.floor(COLS / 2), cy = Math.floor(ROWS / 2);
    snake = [{ x: cx, y: cy }, { x: cx - 1, y: cy }, { x: cx - 2, y: cy }];
    dir = { x: 1, y: 0 };
    nextDir = { x: 1, y: 0 };
    score = 0;
    level = 1;
    eaten = 0;
    gameOver = false;
    paused = false;
    placeFood();
    updateUI();
}

// --- Logique ---
// Avance le serpent d'un case, gère collisions et nourriture
function step() {
    if (paused || gameOver) return;

    dir = nextDir;

    const head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };

    // murs
    if (head.x < 0 || head.x >= COLS || head.y < 0 || head.y >= ROWS) {
        triggerDeath(); return;
    }
    // collision avec soi-même
    if (snake.some(s => s.x === head.x && s.y === head.y)) {
        triggerDeath(); return;
    }

    snake.unshift(head);

    // mange la nourriture
    if (head.x === food.x && head.y === food.y) {
        score += 10 * level;
        eaten++;
        if (score > hiscore) {
            hiscore = score;
            fetch("save_score.php", {
                method: "POST",
                credentials: "include",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                body: new URLSearchParams({
                    score: hiscore,
                    game_id: 2
                })
            });
        }
        spawnParticles(food.x * SZ + SZ / 2, food.y * SZ + SZ / 2, '#5DCAA5');
        const newLevel = Math.floor(eaten / LEVEL_THRESHOLD) + 1;
        if (newLevel !== level) {
            level = newLevel;
            restartTimer();
            board.style.boxShadow = '0 0 18px #5DCAA5';
            setTimeout(() => board.style.boxShadow = '', 400);
        }
        placeFood();
        updateUI();
    } else if (bonus && head.x === bonus.x && head.y === bonus.y) {
        // mange le bonus
        score += 50 * level;
        if (score > hiscore) hiscore = score;
        spawnParticles(bonus.x * SZ + SZ / 2, bonus.y * SZ + SZ / 2, '#EF9F27');
        board.style.boxShadow = '0 0 18px #EF9F27';
        setTimeout(() => board.style.boxShadow = '', 400);
        bonus = null;
        updateUI();
    } else {
        snake.pop();
    }

    // timer bonus
    if (bonus) {
        bonus.timer--;
        if (bonus.timer <= 0) bonus = null;
    }

    render();
}

// Déclenche le game over avec animation
function triggerDeath() {
    gameOver = true;
    clearInterval(stepTimer);
    stopKeepalive();
    board.classList.add('shake');
    setTimeout(() => board.classList.remove('shake'), 300);
    spawnParticles(snake[0].x * SZ + SZ / 2, snake[0].y * SZ + SZ / 2, '#D85A30');
    render();
}

// Redémarre le timer de déplacement avec le bon intervalle
function restartTimer() {
    clearInterval(stepTimer);
    stepTimer = setInterval(step, getInterval());
}

// --- Rendu ---
// Dessine une case du serpent avec reflet et yeux sur la tête
function drawCell(x, y, color, isHead = false) {
    const px = x * SZ, py = y * SZ;
    ctx.fillStyle = color;
    ctx.fillRect(px + 1, py + 1, SZ - 2, SZ - 2);
    // reflet
    ctx.fillStyle = 'rgba(255,255,255,0.15)';
    ctx.fillRect(px + 1, py + 1, SZ - 2, 3);
    // ombre bas
    ctx.fillStyle = 'rgba(0,0,0,0.25)';
    ctx.fillRect(px + 1, py + SZ - 4, SZ - 2, 3);

    if (isHead) {
        // yeux
        const eyeColor = '#04050f';
        const eyeSize = 2;
        if (dir.x === 1) { // droite
            ctx.fillStyle = eyeColor;
            ctx.fillRect(px + SZ - 5, py + 3, eyeSize, eyeSize);
            ctx.fillRect(px + SZ - 5, py + SZ - 5, eyeSize, eyeSize);
        } else if (dir.x === -1) { // gauche
            ctx.fillStyle = eyeColor;
            ctx.fillRect(px + 3, py + 3, eyeSize, eyeSize);
            ctx.fillRect(px + 3, py + SZ - 5, eyeSize, eyeSize);
        } else if (dir.y === -1) { // haut
            ctx.fillStyle = eyeColor;
            ctx.fillRect(px + 3, py + 3, eyeSize, eyeSize);
            ctx.fillRect(px + SZ - 5, py + 3, eyeSize, eyeSize);
        } else { // bas
            ctx.fillStyle = eyeColor;
            ctx.fillRect(px + 3, py + SZ - 5, eyeSize, eyeSize);
            ctx.fillRect(px + SZ - 5, py + SZ - 5, eyeSize, eyeSize);
        }
    }
}

// Dessine la nourriture (cercle rouge)
function drawFood(x, y) {
    const px = x * SZ + SZ / 2, py = y * SZ + SZ / 2, r = SZ / 2 - 2;
    ctx.beginPath();
    ctx.arc(px, py, r, 0, Math.PI * 2);
    ctx.fillStyle = '#D85A30';
    ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.25)';
    ctx.beginPath();
    ctx.arc(px - 2, py - 2, r / 3, 0, Math.PI * 2);
    ctx.fill();
}

// Dessine la pomme bonus (orange, clignote avant disparition)
function drawBonus(x, y, timer) {
    const px = x * SZ + SZ / 2, py = y * SZ + SZ / 2, r = SZ / 2 - 1;
    const alpha = timer < 20 ? timer / 20 : 1;
    ctx.globalAlpha = alpha;
    ctx.beginPath();
    ctx.arc(px, py, r, 0, Math.PI * 2);
    ctx.fillStyle = '#EF9F27';
    ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.beginPath();
    ctx.arc(px - 2, py - 2, r / 3, 0, Math.PI * 2);
    ctx.fill();
    ctx.globalAlpha = 1;
    // croix
    ctx.fillStyle = '#04050f';
    ctx.fillRect(px - 3, py - 1, 6, 2);
    ctx.fillRect(px - 1, py - 3, 2, 6);
}

// Redessine tout le canvas (serpent, nourriture, UI)
function render() {
    ctx.fillStyle = '#04050f';
    ctx.fillRect(0, 0, W, H);

    // grille subtile
    ctx.strokeStyle = 'rgba(0,34,85,0.3)';
    ctx.lineWidth = 0.5;
    for (let c = 0; c < COLS; c++) for (let r = 0; r < ROWS; r++) ctx.strokeRect(c * SZ, r * SZ, SZ, SZ);

    // serpent
    snake.forEach((s, i) => {
        const t = i / snake.length;
        // dégradé de couleur tête → queue
        const r = Math.round(29 + t * (4 - 29));
        const g = Math.round(158 + t * (5 - 158));
        const bv = Math.round(117 + t * (15 - 117));
        drawCell(s.x, s.y, `rgb(${r},${g},${bv})`, i === 0);
    });

    drawFood(food.x, food.y);
    if (bonus) drawBonus(bonus.x, bonus.y, bonus.timer);

    if (gameOver) {
        ctx.fillStyle = 'rgba(4,5,15,0.82)';
        ctx.fillRect(0, H / 2 - 50, W, 100);
        ctx.fillStyle = '#BBDDDD';
        ctx.font = '500 18px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER', W / 2, H / 2 - 10);
        ctx.font = '12px monospace';
        ctx.fillStyle = '#6688aa';
        ctx.fillText('score : ' + score, W / 2, H / 2 + 12);
        ctx.fillText('↵ START pour rejouer', W / 2, H / 2 + 30);
    }

    if (paused && !gameOver) {
        ctx.fillStyle = 'rgba(4,5,15,0.7)';
        ctx.fillRect(0, H / 2 - 25, W, 50);
        ctx.fillStyle = '#BBDDDD';
        ctx.font = '500 16px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('PAUSE', W / 2, H / 2 + 6);
    }
}

// Met à jour score, niveau, longueur dans le DOM
function updateUI() {
    document.getElementById('score-val').textContent = score;
    document.getElementById('hi-score-val').textContent = hiscore;
    document.getElementById('level-val').textContent = level;
    document.getElementById('length-val').textContent = snake.length;
    const progress = ((eaten % LEVEL_THRESHOLD) / LEVEL_THRESHOLD) * 100;
    document.getElementById('level-bar').style.width = progress + '%';
}

// --- Input ---
const DIR_MAP = {
    ArrowLeft: { x: -1, y: 0 }, q: { x: -1, y: 0 }, Q: { x: -1, y: 0 },
    ArrowRight: { x: 1, y: 0 }, d: { x: 1, y: 0 }, D: { x: 1, y: 0 },
    ArrowUp: { x: 0, y: -1 }, z: { x: 0, y: -1 }, Z: { x: 0, y: -1 },
    ArrowDown: { x: 0, y: 1 }, s: { x: 0, y: 1 }, S: { x: 0, y: 1 },
};

document.addEventListener('keydown', e => {
    if (e.key === 'p' || e.key === 'P') { paused = !paused; return; }
    if (e.key === 'Enter' && gameOver) { startGame(); return; }

    const d = DIR_MAP[e.key];
    if (d) {
        e.preventDefault();
        // interdit demi-tour
        if (d.x !== -dir.x || d.y !== -dir.y) nextDir = d;
    }
});

// Lance ou relance une partie
function startGame() {
    clearInterval(stepTimer);
    initGame();
    render();
    stepTimer = setInterval(step, getInterval());
    startKeepalive();
}

document.getElementById('start-btn').addEventListener('click', startGame);

startGame();