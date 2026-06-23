<!-- l'affichage du 2048 -->
<canvas id="effect"></canvas>
        <div id="game-area">
            <div id="grille"></div>

            <div id="side-panel">
                <div class="panel-block">
                    <div class="panel-label">score</div>
                    <div class="panel-value" id="score">0</div>
                </div>
                <div class="panel-block">
                    <div class="panel-label">meilleur</div>
                    <div class="panel-value" id="hi-score-val"><?php echo $hiscore ?? 0; ?></div>
                </div>
                <button id="start-btn">START</button>
                <div id="msg">Z / ↑ : haut<br>S / ↓ : bas<br>Q / ← : gauche<br>D / → : droite</div>
            </div>
        </div>