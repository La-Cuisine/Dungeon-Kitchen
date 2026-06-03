<!-- l'affichage du minesweeper -->
<canvas id="effect"></canvas>

    <div id="game-area">
        <canvas id="board"></canvas>

        <div id="side-panel">
            <div class="panel-block">
                <div class="panel-label">mines</div>
                <div class="panel-value" id="mines-val">0</div>
            </div>
            <div class="panel-block">
                <div class="panel-label">drapeaux</div>
                <div class="panel-value" id="flags-val">0</div>
            </div>
            <div class="panel-block">
                <div class="panel-label">temps</div>
                <div class="panel-value" id="time-val">0</div>
            </div>
            <div class="panel-block">
                <div class="panel-label">meilleur</div>
                <div class="panel-value" id="hi-score-val">--</div>
            </div>
            <div class="panel-block">
                <div class="panel-label">difficulté</div>
                <select id="diff-select">
                    <option value="easy">Facile</option>
                    <option value="medium" selected>Moyen</option>
                    <option value="hard">Difficile</option>
                </select>
            </div>
            <button id="start-btn">START</button>
            <div id="msg">Clic : révéler<br>Clic droit : drapeau<br>1er clic : sûr</div>
        </div>
    </div>