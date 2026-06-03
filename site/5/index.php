<!-- l'affichage du breakout -->
    <canvas id="effect"></canvas>

    <div id="game-area">
        <canvas id="board" width="300" height="500"></canvas>

        <div id="side-panel">
            <div class="panel-block">
                <div class="panel-label">score</div>
                <div class="panel-value" id="score-val">0</div>
            </div>
            <div class="panel-block">
                <div class="panel-label">hi-score</div>
                <div class="panel-value" id="hi-score-val"><?php echo $hiscore; ?></div>
            </div>
            <div class="panel-block">
                <div class="panel-label">vies</div>
                <div class="panel-value" id="lives-val">♥ ♥ ♥</div>
            </div>
            <div class="panel-block">
                <div class="panel-label">niveau</div>
                <div class="panel-value" id="level-val">1</div>
                <div id="level-bar-wrap">
                    <div id="level-bar"></div>
                </div>
            </div>
            <button id="start-btn">START</button>
            <div id="msg">← → ou souris<br>Espace : lancer<br>P : pause</div>
        </div>
    </div>