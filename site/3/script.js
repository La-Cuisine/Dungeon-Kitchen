const W = 300, H = 600;
const board = document.getElementById('board');
const ctx = board.getContext('2d');

// --- Effets de fond (canvas particles) ---
const effc = document.getElementById('effect');
const effctx = effc.getContext('2d');
let particles = [];

function resizeEff() {
    effc.width = window.innerWidth;
    effc.height = window.innerHeight;
}
window.addEventListener('resize', resizeEff);
resizeEff();

//anime les particules
(function animBg() {
    requestAnimationFrame(animBg);
    effctx.fillStyle = 'rgba(4,5,15,0.25)';
    effctx.fillRect(0, 0, effc.width, effc.height);
    particles = particles.filter(p => p.life > 0.02);
    particles.forEach(p => {
        p.x += p.vx; p.y += p.vy; p.life *= 0.92;
        effctx.globalAlpha = p.life;
        effctx.fillStyle = p.color;
        effctx.fillRect(p.x - 2, p.y - 2, 4, 4);
    });
    effctx.globalAlpha = 1;
})();

function spawnParticles(x, y, color) {
    for (let i = 0; i < 14; i++) {
        particles.push({
            x, y,
            vx: (Math.random() - 0.5) * 5,
            vy: (Math.random() - 0.5) * 5,
            life: 1,
            color
        });
    }
}

// --- Sprites aliens (pixel art 11x8) ---
const ALIEN_SPRITES = {
    A: [ // top row - petit alien pointu
        [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0],
        [0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
        [0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0],
    ],
    B: [ // milieu - alien crabe
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0],
        [0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0],
    ],
    C: [ // bas - alien pieuvre
        [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
        [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [0, 0, 1, 1, 0, 0, 0, 1, 1, 0, 0],
        [0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0],
        [1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 1],
    ]
};

const ALIEN_COLORS = { A: '#ED93B1', B: '#5DCAA5', C: '#EF9F27' };
const ALIEN_PTS = { A: 30, B: 20, C: 10 };

// Dimensions alien : sprite 11x8, chaque pixel = 2px => 22x16, marge => cellule 28x22
const SP = 2; // scale pixel
const AW = 11 * SP, AH = 8 * SP;
const CELL_W = AW + 8, CELL_H = AH + 8;
const COLS_ALIENS = 7, ROWS_ALIENS = 3;

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

// --- État du jeu ---
let aliens, player, bullets, enemyBullets;
let score, lives, wave, gameOver, paused;
let hiscore = parseInt(document.querySelector('#hi-score-val').textContent) || 0;
let alienDir, alienSpeed, alienDropping, alienDropY;
let animTick = 0;
let gameLoopId = null;
let lastTime = 0;

// --- Boucliers ---
const SHIELD_COLS = 4, SHIELD_ROWS = 3, SHIELD_SZ = 6;
const SHIELD_POSITIONS = [30, 95, 160, 225]; // x de départ des 4 boucliers
let shields = [];

// Crée les 4 boucliers avec leurs cellules destructibles
function buildShields() {
    shields = SHIELD_POSITIONS.map(sx => {
        const cells = [];
        for (let r = 0; r < SHIELD_ROWS; r++)
            for (let c = 0; c < SHIELD_COLS; c++)
                // trou en bas au centre
                if (!(r === SHIELD_ROWS - 1 && (c === 1 || c === 2)))
                    cells.push({ x: sx + c * SHIELD_SZ, y: 490 + r * SHIELD_SZ, hp: 3 });
        return cells;
    });
}

// Place les aliens en grille selon la vague actuelle
function buildAliens() {
    aliens = [];
    for (let r = 0; r < ROWS_ALIENS; r++) {
        for (let c = 0; c < COLS_ALIENS; c++) {
            const type = r == 0 ? 'A' : r == 1 ? 'B' : 'C';
            aliens.push({
                type,
                x: 10 + c * CELL_W,
                y: 40 + r * CELL_H,
                alive: true,
                frame: 0
            });
        }
    }
    alienDir = 1;
    alienSpeed = 0.4 + (wave - 1) * 0.2;
    alienDropping = false;
    alienDropY = 0;
}

// Initialise score, vies, vague et tous les éléments
function initGame() {
    score = 0;
    lives = 3;
    wave = 1;
    gameOver = false;
    paused = false;
    bullets = [];
    enemyBullets = [];
    player = { x: W / 2 - 10, y: H - 40, w: 20, h: 14, cooldown: 0 };
    buildShields();
    buildAliens();
    updateUI();
}

// --- Dessin ---
// Dessine un alien pixel par pixel (avec animation)
function drawSprite(type, x, y, color, frame) {
    const sprite = ALIEN_SPRITES[type];
    ctx.fillStyle = color;
    sprite.forEach((row, ri) => {
        row.forEach((px, ci) => {
            if (!px) return;
            // animation frame : légère variation
            const oy = (frame % 2 === 0 && (ri === sprite.length - 1)) ? -SP : 0;
            ctx.fillRect(x + ci * SP, y + ri * SP + oy, SP, SP);
        });
    });
}

// Dessine le vaisseau joueur
function drawPlayer() {
    const p = player;
    ctx.fillStyle = '#5DCAA5';
    // corps
    ctx.fillRect(p.x + 2, p.y + 4, p.w - 4, p.h - 4);
    // canon
    ctx.fillRect(p.x + p.w / 2 - 2, p.y, 4, 6);
    // base
    ctx.fillRect(p.x, p.y + p.h - 4, p.w, 4);
    // reflet
    ctx.fillStyle = 'rgba(255,255,255,0.2)';
    ctx.fillRect(p.x + 4, p.y + 5, 4, 2);
}

// Dessine les boucliers avec transparence selon HP
function drawShields() {
    shields.forEach(shield => {
        shield.forEach(cell => {
            const alpha = cell.hp / 3;
            ctx.fillStyle = `rgba(29,158,117,${alpha})`;
            ctx.fillRect(cell.x, cell.y, SHIELD_SZ - 1, SHIELD_SZ - 1);
        });
    });
}

// Dessine les balles du joueur et des ennemis
function drawBullets() {
    ctx.fillStyle = '#BBDDDD';
    bullets.forEach(b => ctx.fillRect(b.x - 1, b.y, 2, 8));
    ctx.fillStyle = '#D85A30';
    enemyBullets.forEach(b => ctx.fillRect(b.x - 1, b.y, 2, 8));
}

// Fond noir + ligne de sol
function drawBackground() {
    ctx.fillStyle = '#04050f';
    ctx.fillRect(0, 0, W, H);
    // ligne sol
    ctx.fillStyle = '#002255';
    ctx.fillRect(0, H - 20, W, 1);
}

// Dessine la ligne de danger en pointillés
function drawUI() {
    // ligne de danger (aliens trop bas)
    ctx.strokeStyle = 'rgba(216,90,48,0.15)';
    ctx.lineWidth = 1;
    ctx.setLineDash([4, 4]);
    ctx.beginPath(); ctx.moveTo(0, H - 60); ctx.lineTo(W, H - 60); ctx.stroke();
    ctx.setLineDash([]);
}

// Redessine tout le canvas
function render() {
    drawBackground();
    drawUI();
    drawShields();
    drawBullets();

    const alive = aliens.filter(a => a.alive);
    alive.forEach(a => {
        drawSprite(a.type, a.x, a.y, ALIEN_COLORS[a.type], animTick);
    });

    drawPlayer();

    if (gameOver) {
        ctx.fillStyle = 'rgba(4,5,15,0.82)';
        ctx.fillRect(0, H / 2 - 55, W, 110);
        ctx.fillStyle = '#BBDDDD';
        ctx.font = '500 22px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('GAME OVER', W / 2, H / 2 - 12);
        ctx.font = '13px monospace';
        ctx.fillStyle = '#6688aa';
        ctx.fillText('score : ' + score, W / 2, H / 2 + 14);
        ctx.fillText('↵ START pour rejouer', W / 2, H / 2 + 34);
    }

    if (paused && !gameOver) {
        ctx.fillStyle = 'rgba(4,5,15,0.7)';
        ctx.fillRect(0, H / 2 - 30, W, 60);
        ctx.fillStyle = '#BBDDDD';
        ctx.font = '500 18px monospace';
        ctx.textAlign = 'center';
        ctx.fillText('PAUSE', W / 2, H / 2 + 7);
    }
}

// --- Logique ---
// Déplace les aliens, gère les bords, descente et tirs ennemis
function updateAliens(dt) {
    const alive = aliens.filter(a => a.alive);
    if (!alive.length) { nextWave(); return; }

    if (alienDropping) {
        aliens.forEach(a => { if (a.alive) a.y += 2; });
        alienDropY += 1;
        if (alienDropY >= CELL_H / 100) { alienDropping = false; alienDir *= -1; alienDropY = 0; }
        return;
    }

    const move = alienSpeed * alienDir * dt * 0.06;
    aliens.forEach(a => { if (a.alive) a.x += move; });

    // bord
    const minX = Math.min(...alive.map(a => a.x));
    const maxX = Math.max(...alive.map(a => a.x + AW));
    if (maxX >= W - 4 || minX <= 4) {
        alienDropping = true;
        alienDropY = 0;
    }

    // alien trop bas => game over
    if (Math.max(...alive.map(a => a.y + AH)) >= H - 60) {
        triggerGameOver();
        return;
    }

    // tir ennemi aléatoire
    if (Math.random() < 0.004 + wave * 0.002) {
        const shooter = alive[Math.floor(Math.random() * alive.length)];
        enemyBullets.push({ x: shooter.x + AW / 2, y: shooter.y + AH, speed: 3 + wave * 0.4 });
    }
}

// Déplace les balles, gère toutes les collisions
function updateBullets(dt) {
    bullets = bullets.filter(b => b.y > 0);
    bullets.forEach(b => b.y -= 7);

    enemyBullets = enemyBullets.filter(b => b.y < H);
    enemyBullets.forEach(b => b.y += b.speed);

    // balles joueur vs aliens
    bullets.forEach((b, bi) => {
        aliens.forEach(a => {
            if (!a.alive) return;
            if (b.x > a.x && b.x < a.x + AW && b.y > a.y && b.y < a.y + AH) {
                a.alive = false;
                score += ALIEN_PTS[a.type];
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
                            game_id: 3
                        })
                    });
                }
                spawnParticlesOnBoard(a.x + AW / 2, a.y + AH / 2, ALIEN_COLORS[a.type]);
                bullets.splice(bi, 1);
                updateUI();
                // accélère les aliens restants
                alienSpeed += 0.08;
            }
        });
    });

    // balles joueur vs boucliers
    bullets.forEach((b, bi) => {
        shields.forEach(shield => {
            shield.forEach((cell, ci) => {
                if (b.x >= cell.x && b.x <= cell.x + SHIELD_SZ && b.y >= cell.y && b.y <= cell.y + SHIELD_SZ) {
                    cell.hp--;
                    if (cell.hp <= 0) shield.splice(ci, 1);
                    bullets.splice(bi, 1);
                }
            });
        });
    });

    // balles ennemies vs boucliers
    enemyBullets.forEach((b, bi) => {
        shields.forEach(shield => {
            shield.forEach((cell, ci) => {
                if (b.x >= cell.x && b.x <= cell.x + SHIELD_SZ && b.y >= cell.y && b.y <= cell.y + SHIELD_SZ) {
                    cell.hp--;
                    if (cell.hp <= 0) shield.splice(ci, 1);
                    enemyBullets.splice(bi, 1);
                }
            });
        });
    });

    // balles ennemies vs joueur
    enemyBullets.forEach((b, bi) => {
        const p = player;
        if (b.x > p.x && b.x < p.x + p.w && b.y > p.y && b.y < p.y + p.h) {
            enemyBullets.splice(bi, 1);
            loseLife();
        }
    });
}

// Convertit coordonnées board → page pour les particules
function spawnParticlesOnBoard(bx, by, color) {
    // convertit coordonnées board -> page pour le canvas effet
    const rect = board.getBoundingClientRect();
    const px = rect.left + bx * (rect.width / W);
    const py = rect.top + by * (rect.height / H);
    spawnParticles(px, py, color);
}

// Déplace le joueur et gère le tir
function updatePlayer(dt) {
    if (keys['ArrowLeft'] || keys['q'] || keys['Q']) player.x = Math.max(0, player.x - 4);
    if (keys['ArrowRight'] || keys['d'] || keys['D']) player.x = Math.min(W - player.w, player.x + 4);

    if (player.cooldown > 0) player.cooldown--;

    if ((keys[' '] || keys['ArrowUp'] || keys['z'] || keys['Z']) && player.cooldown === 0) {
        bullets.push({ x: player.x + player.w / 2, y: player.y });
        player.cooldown = 18;
    }
}

// Enlève une vie, shake + particules, vérifie game over
function loseLife() {
    lives--;
    spawnParticlesOnBoard(player.x + player.w / 2, player.y, '#5DCAA5');
    board.classList.add('shake');
    setTimeout(() => board.classList.remove('shake'), 400);
    updateUI();
    if (lives <= 0) triggerGameOver();
}

// Passe en état game over et redessine
function triggerGameOver() {
    gameOver = true;
    stopKeepalive();
    render();
}

// Lance la vague suivante, reconstruit aliens et boucliers
function nextWave() {
    wave++;
    bullets = [];
    enemyBullets = [];
    buildShields();
    buildAliens();
    updateUI();
    // flash
    board.style.boxShadow = '0 0 24px #5DCAA5';
    setTimeout(() => board.style.boxShadow = '', 500);
}

// Met à jour score, vague, vies dans le DOM
function updateUI() {
    document.getElementById('score-val').textContent = score;
    document.getElementById('wave-val').textContent = wave;
    document.getElementById('hi-score-val').textContent = hiscore;
    const hearts = '♥ '.repeat(lives).trim() || '—';
    document.getElementById('lives-val').textContent = hearts;
    const alive = aliens.filter(a => a.alive).length;
    const total = COLS_ALIENS * ROWS_ALIENS;
    document.getElementById('wave-bar').style.width = Math.round((alive / total) * 100) + '%';
}

// --- Input ---
const keys = {};
document.addEventListener('keydown', e => {
    keys[e.key] = true;
    if (e.key === ' ') e.preventDefault();
    if (e.key === 'p' || e.key === 'P') paused = !paused;
    if ((e.key === 'Enter') && gameOver) startGame();
});
document.addEventListener('keyup', e => { keys[e.key] = false; });

// --- Boucle de jeu ---
// Boucle principale (requestAnimationFrame)
function gameLoop(ts) {
    const dt = Math.min(ts - lastTime, 50);
    lastTime = ts;
    animTick = Math.floor(ts / 600) % 2;

    if (!paused && !gameOver) {
        updatePlayer(dt);
        updateAliens(dt);
        updateBullets(dt);
    }
    render();
    gameLoopId = requestAnimationFrame(gameLoop);
}

// Lance ou relance une partie
function startGame() {
    if (gameLoopId) cancelAnimationFrame(gameLoopId);
    initGame();
    lastTime = performance.now();
    gameLoopId = requestAnimationFrame(gameLoop);
    startKeepalive();
}

document.getElementById('start-btn').addEventListener('click', startGame);

startGame();