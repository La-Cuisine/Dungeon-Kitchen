<!-- l'affichage du snake -->
    <canvas id="effect"></canvas>

    <div id="game-area">
        <canvas id="board" width="300" height="300"></canvas>

        <div id="side-panel">
            <div class="panel-block">
                <div class="panel-label">score</div>
                <div class="panel-value" id="score-val">0</div>
            </div>
            <div class="panel-block">
                <div class="panel-label">hi-score</div>
                <div class="panel-value" id="hi-score-val"><?php echo $hiscore;?></div>
            </div>
            <div class="panel-block">
                <div class="panel-label">niveau</div>
                <div class="panel-value" id="level-val">1</div>
                <div id="level-bar-wrap"><div id="level-bar"></div></div>
            </div>
            <div class="panel-block">
                <div class="panel-label">longueur</div>
                <div class="panel-value" id="length-val">1</div>
            </div>
            <button id="start-btn">START</button>
            <div id="msg">← → ↑ ↓ bouger<br>ZQSD aussi<br>P : pause</div>
        </div>
    </div>

