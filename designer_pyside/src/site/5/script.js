const W = 300, H = 500;
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
        p.x += p.vx; p.y += p.vy; p.vy += 0.08; p.life *= 0.92;
        effctx.globalAlpha = p.life;
        effctx.fillStyle = p.color;
        effctx.fillRect(p.x - 2, p.y - 2, 4, 4);
        effctx.globalAlpha = 1;
    });
})();

function spawnParticles(bx, by, color) {
    const rect = board.getBoundingClientRect();
    const px = rect.left + bx * (rect.width / W);
    const py = rect.top + by * (rect.height / H);
    for (let i = 0; i < 10; i++) particles.push({
        x: px, y: py,
        vx: (Math.random() - 0.5) * 5,
        vy: (Math.random() - 1) * 4,
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

// --- Config briques ---
const BRICK_COLS = 10, BRICK_ROWS = 6;
const BRICK_W = W / BRICK_COLS, BRICK_H = 14;
const BRICK_OFFSET_Y = 40;

const ROW_COLORS = [
    '#ED93B1', // rose
    '#D85A30', // orange
    '#EF9F27', // ambre
    '#5DCAA5', // teal
    '#378ADD', // bleu
    '#AFA9EC', // violet
];
const ROW_PTS = [60, 50, 40, 30, 20, 10];

// --- État ---
let bricks, paddle, ball, score, lives, level, gameOver, paused, launched;
let hiscore = parseInt(document.querySelector('#hi-score-val').textContent) || 0;
let animId = null;
const keys = {};

// Paddle
const PAD_H = 8, PAD_Y = H - 30;
let PAD_W = 50;

function getPadSpeed() { return 5 + level * 0.5; }
function getBallSpeed() { return 3.5 + level * 0.4; }

// Génère toutes les briques selon le niveau (certaines ont 2 HP)
function buildBricks() {
    bricks = [];
    for (let r = 0; r < BRICK_ROWS; r++) {
        for (let c = 0; c < BRICK_COLS; c++) {
            // niveau > 3 : certaines briques ont 2 HP
            const hp = (level >= 3 && Math.random() < 0.2) ? 2 : 1;
            bricks.push({
                x: c * BRICK_W + 2,
                y: BRICK_OFFSET_Y + r * (BRICK_H + 3),
                w: BRICK_W - 4,
                h: BRICK_H,
                color: ROW_COLORS[r],
                pts: ROW_PTS[r],
                hp,
                maxHp: hp,
                alive: true
            });
        }
    }
}

// Replace la balle sur la raquette, en attente de lancement
function resetBall() {
    launched = false;
    ball = {
        x: paddle.x + PAD_W / 2,
        y: PAD_Y - 8,
        r: 5,
        vx: 0,
        vy: 0,
    };
}

// Lance la balle dans une direction aléatoire vers le haut
function launchBall() {
    if (launched) return;
    launched = true;
    const spd = getBallSpeed();
    const angle = -Math.PI / 2 + (Math.random() - 0.5) * Math.PI / 3;
    ball.vx = Math.cos(angle) * spd;
    ball.vy = Math.sin(angle) * spd;
}

// Initialise score, vies, niveau et tous les éléments
function initGame() {
    score = 0; lives = 3; level = 1; gameOver = false; paused = false;
    PAD_W = 50;
    paddle = { x: W / 2 - PAD_W / 2, y: PAD_Y };
    buildBricks();
    resetBall();
    updateUI();
}

// --- Logique ---
// Logique principale : déplacements, collisions balle/briques/raquette
function update() {
    if (paused || gameOver) return;

    // déplacement paddle clavier
    if (keys['ArrowLeft'] || keys['q'] || keys['Q']) paddle.x = Math.max(0, paddle.x - getPadSpeed());
    if (keys['ArrowRight'] || keys['d'] || keys['D']) paddle.x = Math.min(W - PAD_W, paddle.x + getPadSpeed());

    if (!launched) {
        ball.x = paddle.x + PAD_W / 2;
        return;
    }

    ball.x += ball.vx;
    ball.y += ball.vy;

    // murs gauche / droite
    if (ball.x - ball.r <= 0) { ball.x = ball.r; ball.vx = Math.abs(ball.vx); }
    if (ball.x + ball.r >= W) { ball.x = W - ball.r; ball.vx = -Math.abs(ball.vx); }
    // plafond
    if (ball.y - ball.r <= 0) { ball.y = ball.r; ball.vy = Math.abs(ball.vy); }

    // balle perdue
    if (ball.y + ball.r >= H + 10) {
        lives--;
        spawnParticles(ball.x, H - 10, '#D85A30');
        board.classList.add('shake');
        setTimeout(() => board.classList.remove('shake'), 300);
        updateUI();
        if (lives <= 0) { gameOver = true; stopKeepalive(); render(); return; }
        resetBall();
        return;
    }

    // paddle
    if (
        ball.vy > 0 &&
        ball.y + ball.r >= paddle.y &&
        ball.y + ball.r <= paddle.y + PAD_H + 4 &&
        ball.x >= paddle.x - ball.r &&
        ball.x <= paddle.x + PAD_W + ball.r
    ) {
        ball.vy = -Math.abs(ball.vy);
        // angle selon position sur le paddle
        const rel = (ball.x - paddle.x) / PAD_W; // 0..1
        const angle = (rel - 0.5) * Math.PI * 0.7;
        const spd = Math.sqrt(ball.vx * ball.vx + ball.vy * ball.vy);
        ball.vx = Math.sin(angle) * spd;
        ball.vy = -Math.cos(angle) * spd;
        ball.y = paddle.y - ball.r - 1;
    }

    // briques
    for (let i = 0; i < bricks.length; i++) {
        const b = bricks[i];
        if (!b.alive) continue;

        const closestX = Math.max(b.x, Math.min(ball.x, b.x + b.w));
        const closestY = Math.max(b.y, Math.min(ball.y, b.y + b.h));
        const dx = ball.x - closestX, dy = ball.y - closestY;

        if (dx * dx + dy * dy < ball.r * ball.r) {
            b.hp--;
            if (b.hp <= 0) {
                b.alive = false;
                score += b.pts * level;
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
                            game_id: 5
                        })
                    });
                }
                spawnParticles(b.x + b.w / 2, b.y + b.h / 2, b.color);
            } else {
                // brique endommagée : flash
                spawnParticles(b.x + b.w / 2, b.y + b.h / 2, '#BBDDDD');
            }

            // rebond : côté ou dessus/dessous
            const overlapX = ball.r - Math.abs(dx);
            const overlapY = ball.r - Math.abs(dy);
            if (overlapX < overlapY) ball.vx = -ball.vx;
            else ball.vy = -ball.vy;

            updateUI();

            // toutes les briques détruites → niveau suivant
            if (bricks.every(br => !br.alive)) { nextLevel(); return; }
            break;
        }
    }
}

// Passe au niveau suivant, réduit la raquette, reconstruit les briques
function nextLevel() {
    level++;
    PAD_W = Math.max(30, PAD_W - 3);
    buildBricks();
    resetBall();
    board.style.boxShadow = '0 0 24px #5DCAA5';
    setTimeout(() => board.style.boxShadow = '', 600);
    updateUI();
}

// --- Rendu ---
// Dessine toutes les briques vivantes avec reflet et indicateur HP
function drawBricks() {
    bricks.forEach(b => {
        if (!b.alive) return;
        const alpha = b.hp < b.maxHp ? 0.5 : 1;
        ctx.globalAlpha = alpha;
        ctx.fillStyle = b.color;
        ctx.fillRect(b.x, b.y, b.w, b.h);
        // reflet
        ctx.fillStyle = 'rgba(255,255,255,0.18)';
        ctx.fillRect(b.x, b.y, b.w, 3);
        ctx.fillStyle = 'rgba(0,0,0,0.2)';
        ctx.fillRect(b.x, b.y + b.h - 3, b.w, 3);
        // HP indicator
        if (b.maxHp > 1 && b.hp > 1) {
            ctx.fillStyle = 'rgba(255,255,255,0.5)';
            ctx.font = '8px monospace';
            ctx.textAlign = 'center';
            ctx.textBaseline = 'middle';
            ctx.fillText('2', b.x + b.w / 2, b.y + b.h / 2);
        }
        ctx.globalAlpha = 1;
    });
}

// Dessine la raquette
function drawPaddle() {
    const p = paddle;
    ctx.fillStyle = '#5DCAA5';
    ctx.fillRect(p.x, p.y, PAD_W, PAD_H);
    ctx.fillStyle = 'rgba(255,255,255,0.2)';
    ctx.fillRect(p.x, p.y, PAD_W, 3);
    ctx.fillStyle = 'rgba(0,0,0,0.2)';
    ctx.fillRect(p.x, p.y + PAD_H - 2, PAD_W, 2);
}

// Dessine la balle + ligne de trajectoire si pas encore lancée
function drawBall() {
    ctx.beginPath();
    ctx.arc(ball.x, ball.y, ball.r, 0, Math.PI * 2);
    ctx.fillStyle = '#BBDDDD';
    ctx.fill();
    ctx.fillStyle = 'rgba(255,255,255,0.4)';
    ctx.beginPath();
    ctx.arc(ball.x - 1, ball.y - 1, ball.r / 3, 0, Math.PI * 2);
    ctx.fill();

    // trait de trajectoire si pas encore lancé
    if (!launched) {
        ctx.strokeStyle = 'rgba(187,221,221,0.2)';
        ctx.lineWidth = 1;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(ball.x, ball.y);
        ctx.lineTo(ball.x, BRICK_OFFSET_Y + BRICK_ROWS * (BRICK_H + 3));
        ctx.stroke();
        ctx.setLineDash([]);
    }
}

// Redessine tout le canvas
function render() {
    ctx.fillStyle = '#04050f';
    ctx.fillRect(0, 0, W, H);

    // grille subtile
    ctx.strokeStyle = 'rgba(0,34,85,0.2)';
    ctx.lineWidth = 0.5;
    for (let x = 0; x < W; x += 30) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = 0; y < H; y += 30) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }

    drawBricks();
    drawPaddle();
    drawBall();

    if (!launched && !gameOver) {
        ctx.fillStyle = 'rgba(187,221,221,0.4)';
        ctx.font = '11px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('ESPACE pour lancer', W / 2, H - 10);
    }

    if (gameOver) {
        ctx.fillStyle = 'rgba(4,5,15,0.85)';
        ctx.fillRect(0, H / 2 - 50, W, 100);
        ctx.fillStyle = '#BBDDDD';
        ctx.font = '500 22px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('GAME OVER', W / 2, H / 2 - 10);
        ctx.font = '12px monospace';
        ctx.fillStyle = '#6688aa';
        ctx.fillText('score : ' + score, W / 2, H / 2 + 14);
        ctx.fillText('START pour rejouer', W / 2, H / 2 + 32);
    }

    if (paused && !gameOver) {
        ctx.fillStyle = 'rgba(4,5,15,0.7)';
        ctx.fillRect(0, H / 2 - 25, W, 50);
        ctx.fillStyle = '#BBDDDD';
        ctx.font = '500 16px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('PAUSE', W / 2, H / 2);
    }
}

// Met à jour score, vies, niveau dans le DOM
function updateUI() {
    document.getElementById('score-val').textContent = score;
    document.getElementById('hi-score-val').textContent = hiscore;
    document.getElementById('lives-val').textContent = '♥ '.repeat(lives).trim() || '—';
    document.getElementById('level-val').textContent = level;
    const alive = bricks.filter(b => b.alive).length;
    const total = BRICK_COLS * BRICK_ROWS;
    document.getElementById('level-bar').style.width = Math.round((1 - alive / total) * 100) + '%';
}

// --- Game loop ---
// Boucle principale (requestAnimationFrame)
function gameLoop() {
    update();
    render();
    animId = requestAnimationFrame(gameLoop);
}

// Lance ou relance une partie
function startGame() {
    if (animId) cancelAnimationFrame(animId);
    initGame();
    board.style.boxShadow = '';
    startKeepalive();
    gameLoop();
}

// --- Input ---
document.addEventListener('keydown', e => {
    keys[e.key] = true;
    if (e.key === ' ') { e.preventDefault(); launchBall(); }
    if (e.key === 'p' || e.key === 'P') paused = !paused;
    if (e.key === 'Enter' && gameOver) startGame();
});
document.addEventListener('keyup', e => { keys[e.key] = false; });

// souris
board.addEventListener('mousemove', e => {
    const rect = board.getBoundingClientRect();
    const scaleX = W / rect.width;
    const mx = (e.clientX - rect.left) * scaleX;
    paddle.x = Math.max(0, Math.min(W - PAD_W, mx - PAD_W / 2));
});

board.addEventListener('click', () => launchBall());

document.getElementById('start-btn').addEventListener('click', startGame);

startGame();