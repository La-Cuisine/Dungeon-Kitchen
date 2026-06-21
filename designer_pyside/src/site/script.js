//au chargement de la page load les btn du nav et build la grille du tetris dans featured-banner
document.addEventListener('DOMContentLoaded', function () {
    navbtn();
    buildTetrisGrid();
});

//quand le bouton connexion est appuis nous donne les champs pour se connecter
function navbtn() {
    if (document.querySelector('.nav-btn') != null)
        document.querySelector('.nav-btn').addEventListener("click", () => {
            document.querySelector('#connexion-form').removeAttribute('style');
            document.querySelector('.nav-btn').setAttribute('style', "display: none");
            document.querySelector('#err-log').setAttribute('style', "display: none");
        });
}

//les filtre à apliquer dans la game grid pour afficher les jeux
function filterGames(category, btn) {
    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.game-card').forEach(card => {
        const show = category === 'all' || card.dataset.category === category;
        card.style.display = show ? 'block' : 'none';
    });
}

// tetris visual show
function buildTetrisGrid() {
    const grid = document.getElementById('tetrisGrid');
    if (!grid) return;
    const colors = [
        '#00f5ff', '#ff00aa', '#ffe600', '#39ff14', '#ff6b35', '#bf00ff',
        '#00f5ff', 'transparent', 'transparent', 'transparent',
        '#ff00aa', '#ffe600', 'transparent', 'transparent', 'transparent',
    ];
    const rows = 8, cols = 5;
    grid.style.gridTemplateColumns = `repeat(${cols}, 1fr)`;
    for (let i = 0; i < rows * cols; i++) {
        const cell = document.createElement('div');
        cell.classList.add('tetris-block');
        const roll = Math.random();
        if (roll > 0.55) {
            const c = ['#00f5ff', '#ff00aa', '#ffe600', '#39ff14', '#ff6b35', '#bf00ff'][Math.floor(Math.random() * 6)];
            cell.style.background = c;
            cell.style.boxShadow = `0 0 8px ${c}`;
        } else {
            cell.style.background = 'rgba(255,255,255,0.04)';
            cell.style.border = '1px solid rgba(255,255,255,0.05)';
        }
        grid.appendChild(cell);
    }

    // animate blocks
    setInterval(() => {
        const blocks = grid.querySelectorAll('.tetris-block');
        const idx = Math.floor(Math.random() * blocks.length);
        const c = ['#00f5ff', '#ff00aa', '#ffe600', '#39ff14', '#ff6b35', '#bf00ff'][Math.floor(Math.random() * 6)];
        const b = blocks[idx];
        if (Math.random() > 0.5) {
            b.style.background = c;
            b.style.boxShadow = `0 0 8px ${c}`;
            b.style.border = 'none';
        } else {
            b.style.background = 'rgba(255,255,255,0.04)';
            b.style.boxShadow = 'none';
            b.style.border = '1px solid rgba(255,255,255,0.05)';
        }
    }, 300);
}