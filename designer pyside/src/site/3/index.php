<!-- l'affichage du space invader -->
    <canvas id="effect"></canvas>

    <div id="game-area">
        <canvas id="board" width="300" height="600"></canvas>

        <div id="side-panel">
            <div class="panel-block">
                <div class="panel-label">score</div>
                <div class="panel-value" id="score-val">0</div>
            </div>
            <div class="panel-block">
                <div class="panel-label">vague</div>
                <div class="panel-value" id="wave-val">1</div>
                <div id="wave-bar-wrap"><div id="wave-bar"></div></div>
            </div>
            <div class="panel-block">
                <div class="panel-label">vies</div>
                <div class="panel-value" id="lives-val">&#9829; &#9829; &#9829;</div>
            </div>
            <div class="panel-block">
                <div class="panel-label">hi-score</div>
                <div class="panel-value" id="hi-score-val"><?php echo $hiscore;?></div>
            </div>
            <button id="start-btn">START</button>
            <div id="msg">← → bouger<br>Espace : tirer<br>P : pause</div>
        </div>
    </div>