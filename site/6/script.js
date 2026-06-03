let score = 0;
let nbVide = 16;
let gm_over = 0;
let audio = new Audio("./6/slot_machine_CharlottePollock.mp3");
audio.currentTime = 1;
let timeoutid;

let hiscore = parseInt(document.getElementById('hi-score-val').textContent) || 0;

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

let tab = [];
for (let i = 0; i < 4; i++) {
    tab[i] = [];
    for (let j = 0; j < 4; j++) {
        tab[i][j] = 0;
    }
}

// Construit le DOM de la grille 4x4
function construiregrille() {
    let b = document.getElementById("grille");

    for (let i = 0; i < 4; i++) {
        let c = document.createElement("span");
        c.innerHTML = " ";
        c.setAttribute("id", i);
        b.appendChild(c);
        b.appendChild(document.createElement("br"));
    }
    for (let i = 0; i < 4; i++) {
        c = document.getElementById(i);
        for (let j = 0; j < 4; j++) {
            let p = document.createElement("span");
            p.innerHTML = tab[i][j] == 0 ? "&#8199;&#8199;" : tab[i][j];
            p.setAttribute("id", "[" + i + "][" + j + "]");
            p.setAttribute("class", "cell");
            c.appendChild(p);
        }
    }
}

// Met à jour le score affiché et sauvegarde le hiscore en DB si battu
function afficher_score() {
    document.getElementById("score").innerHTML = score;

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
                game_id: 6
            })
        });
    }
    document.getElementById("hi-score-val").textContent = hiscore;
}

// Place une valeur dans une case (tableau + DOM)
function caseVide(i, x) {
    if (i < nbVide) {
        let row, col;
        if (i < 4) { row = 0; col = i; }
        else if (i < 8) { row = 1; col = i % 4; }
        else if (i < 12) { row = 2; col = i % 4; }
        else { row = 3; col = i % 4; }

        tab[row][col] = x;
        let p = document.getElementById("[" + row + "][" + col + "]");
        p.innerHTML = x == 0 ? "&#8199;&#8199;" : x;
    }
}

// Récupère la valeur d'une case par index linéaire (0-15)
function get_tab(i) {
    if (i < 4) return tab[0][i];
    if (i < 8) return tab[1][i % 4];
    if (i < 12) return tab[2][i % 4];
    if (i < nbVide) return tab[3][i % 4];
}

// Réinitialise la grille et place 2 tuiles de départ
function nouvelle() {
    for (let i = 0; i < 4; i++)
        for (let j = 0; j < 4; j++)
            tab[i][j] = 0;

    score = 0;
    gm_over = 0;

    document.getElementById("grille").innerHTML = '';
    construiregrille();
    afficher_score();
    startKeepalive();

    for (let i = 0; i < 2; i++) {
        let tmp = Math.floor(Math.random() * nbVide);
        if (get_tab(tmp) == 0) {
            caseVide(tmp, 2);
        } else {
            i -= 1;
        }
    }
}

// Joue l'animation + son lors d'une fusion de tuiles
function animation() {
    document.getElementById("grille").setAttribute("class", "grid_anim");
    let ces = document.getElementsByClassName("cell");
    Array.from(ces).forEach((c) => c.setAttribute("class", "cell_bob"));

    if (audio.currentTime >= 4.25) audio.currentTime = 1;
    clearTimeout(timeoutid);
    audio.play();

    setTimeout(() => {
        document.getElementById("grille").removeAttribute("class");
        let ces = document.getElementsByClassName("cell_bob");
        Array.from(ces).forEach((c) => c.setAttribute("class", "cell"));
    }, 150 + Math.floor(Math.random() * 100));

    timeoutid = setTimeout(() => audio.pause(), 1100);
}

// Fait glisser et fusionner toutes les tuiles direction gauche
function glisse_g() {
    for (let i = 0; i < 4; i++) {
        let v = 0;
        for (let j = 0; j < 4; j++) {
            let p = document.getElementById("[" + i + "][" + j + "]");
            if (tab[i][j] == 0) {
                ++v;
            } else if (tab[i][j - v - 1] == 0) {
                let q = document.getElementById("[" + i + "][" + (j - v - 1) + "]");
                tab[i][j - v - 1] = tab[i][j]; tab[i][j] = 0;
                p.innerHTML = "&#8199;&#8199;"; q.innerHTML = tab[i][j - v - 1];
                ++v;
            } else if (tab[i][j - v - 1] == tab[i][j]) {
                let q = document.getElementById("[" + i + "][" + (j - v - 1) + "]");
                tab[i][j - v - 1] += tab[i][j]; score += tab[i][j - v - 1];
                tab[i][j] = 0;
                p.innerHTML = "&#8199;&#8199;"; q.innerHTML = tab[i][j - v - 1];
                animation(); ++v;
            } else if (tab[i][j - v - 1] != tab[i][j] && tab[i][j - v - 1] != 0 && v > 0) {
                let q = document.getElementById("[" + i + "][" + (j - v) + "]");
                tab[i][j - v] = tab[i][j]; tab[i][j] = 0;
                p.innerHTML = "&#8199;&#8199;"; q.innerHTML = tab[i][j - v];
            }
        }
    }
}

// Fait glisser et fusionner toutes les tuiles direction droite
function glisse_d() {
    for (let i = 3; i >= 0; i--) {
        let v = 0;
        for (let j = 3; j >= 0; j--) {
            let p = document.getElementById("[" + i + "][" + j + "]");
            if (tab[i][j] == 0) {
                ++v;
            } else if (tab[i][j + v + 1] == 0) {
                let q = document.getElementById("[" + i + "][" + (j + v + 1) + "]");
                tab[i][j + v + 1] = tab[i][j]; tab[i][j] = 0;
                p.innerHTML = "&#8199;&#8199;"; q.innerHTML = tab[i][j + v + 1];
                ++v;
            } else if (tab[i][j + v + 1] == tab[i][j]) {
                let q = document.getElementById("[" + i + "][" + (j + v + 1) + "]");
                tab[i][j + v + 1] += tab[i][j]; score += tab[i][j + v + 1];
                tab[i][j] = 0;
                p.innerHTML = "&#8199;&#8199;"; q.innerHTML = tab[i][j + v + 1];
                animation(); ++v;
            } else if (tab[i][j + v + 1] != tab[i][j] && tab[i][j + v + 1] != 0 && v > 0) {
                let q = document.getElementById("[" + i + "][" + (j + v) + "]");
                tab[i][j + v] = tab[i][j]; tab[i][j] = 0;
                p.innerHTML = "&#8199;&#8199;"; q.innerHTML = tab[i][j + v];
            }
        }
    }
}

// Fait glisser et fusionner toutes les tuiles direction haut
function glisse_h() {
    for (let i = 0; i < 4; i++) {
        let v = 0;
        for (let j = 0; j < 4; j++) {
            let p = document.getElementById("[" + j + "][" + i + "]");
            if (tab[j][i] == 0 || j == 0) {
                ++v;
            } else if (tab[j - v][i] == 0) {
                let q = document.getElementById("[" + (j - v) + "][" + i + "]");
                tab[j - v][i] = tab[j][i]; tab[j][i] = 0;
                p.innerHTML = "&#8199;&#8199;"; q.innerHTML = tab[j - v][i];
                ++v;
            } else if (tab[j - v][i] == tab[j][i] && j - v != j) {
                let q = document.getElementById("[" + (j - v) + "][" + i + "]");
                tab[j - v][i] += tab[j][i]; score += tab[j - v][i];
                tab[j][i] = 0;
                p.innerHTML = "&#8199;&#8199;"; q.innerHTML = tab[j - v][i];
                animation(); ++v;
            } else if (tab[j - v][i] != 0 && tab[j - v + 1][i] == 0 && tab[j - v][i] != tab[j][i]) {
                let q = document.getElementById("[" + (j - v + 1) + "][" + i + "]");
                tab[j - v + 1][i] = tab[j][i]; tab[j][i] = 0;
                p.innerHTML = "&#8199;&#8199;"; q.innerHTML = tab[j - v + 1][i];
            }
        }
    }
}

// Fait glisser et fusionner toutes les tuiles direction bas
function glisse_b() {
    for (let i = 3; i >= 0; i--) {
        let v = 0;
        for (let j = 3; j >= 0; j--) {
            let p = document.getElementById("[" + j + "][" + i + "]");
            if (tab[j][i] == 0 || j == 3) {
                ++v;
            } else if (tab[j + v][i] == 0) {
                let q = document.getElementById("[" + (j + v) + "][" + i + "]");
                tab[j + v][i] = tab[j][i]; tab[j][i] = 0;
                p.innerHTML = "&#8199;&#8199;"; q.innerHTML = tab[j + v][i];
                ++v;
            } else if (tab[j + v][i] == tab[j][i] && j + v != j) {
                let q = document.getElementById("[" + (j + v) + "][" + i + "]");
                tab[j + v][i] += tab[j][i]; score += tab[j + v][i];
                tab[j][i] = 0;
                p.innerHTML = "&#8199;&#8199;"; q.innerHTML = tab[j + v][i];
                animation(); ++v;
            } else if (tab[j + v][i] != 0 && tab[j + v - 1][i] == 0 && tab[j + v][i] != tab[j][i]) {
                let q = document.getElementById("[" + (j + v - 1) + "][" + i + "]");
                tab[j + v - 1][i] = tab[j][i]; tab[j][i] = 0;
                p.innerHTML = "&#8199;&#8199;"; q.innerHTML = tab[j + v - 1][i];
            }
        }
    }
}

// Dispatch vers la bonne direction selon la touche pressée
function glisse(e) {
    if (e == "q" || e == "ArrowLeft" || e == "Q") glisse_g();
    else if (e == "d" || e == "ArrowRight" || e == "D") glisse_d();
    else if (e == "z" || e == "ArrowUp" || e == "Z") glisse_h();
    else if (e == "s" || e == "ArrowDown" || e == "S") glisse_b();
}

// Place une nouvelle tuile "2" sur une case vide aléatoire
function new_elem() {
    let i = 1;
    while (i == 1 && gm_over == 0) {
        let tmp = Math.floor(Math.random() * nbVide);
        if (get_tab(tmp) == 0) {
            caseVide(tmp, 2);
            i = 0;
        }
    }
}

// Vérifie si la grille est entièrement remplie
function is_full() {
    for (let i = 0; i < 4; i++)
        for (let j = 0; j < 4; j++)
            if (tab[i][j] == 0) return false;
    return true;
}

// Envoie le score actuel en DB
function saveScore() {
    fetch("save_score.php", {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        credentials: "include",
        body: new URLSearchParams({
            score: score,
            game_id: 6
        })
    });
}

// Vérifie et déclenche le game over si la grille est pleine
function game_over() {
    if (is_full()) {
        gm_over = 1;
        stopKeepalive();
        saveScore();
        document.getElementById("score").innerHTML = score + "<br>GAME OVER";
    }
}

document.addEventListener('DOMContentLoaded', function () {
    construiregrille();
    afficher_score();
    document.querySelector('#start-btn').addEventListener("click", () => {
        nouvelle();
    });
});

window.addEventListener("load", () => {
    nouvelle();
    window.addEventListener("keydown", (e) => {
        if (gm_over == 0) {
            glisse(e.key);
            if (e.key == "q" || e.key == "ArrowLeft" ||
                e.key == "d" || e.key == "ArrowRight" ||
                e.key == "z" || e.key == "ArrowUp" ||
                e.key == "s" || e.key == "ArrowDown") {
                new_elem();
                afficher_score();
                game_over();
            }
        }
    });
});