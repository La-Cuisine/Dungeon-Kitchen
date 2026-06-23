<!-- l'affichage du tetris -->
        <div id="app">
            <canvas id="effect"></canvas>
            <div id="game-area">
                <canvas id="board" width="300" height="600"></canvas>
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
                        <div id="level-bar-wrap">
                            <div id="level-bar"></div>
                        </div>
                    </div>
                    <div class="panel-block">
                        <div class="panel-label">lignes</div>
                        <div class="panel-value" id="lines-val">0</div>
                    </div>
                    <div class="panel-block">
                        <div class="panel-label">suivant</div>
                        <canvas id="next-canvas" width="80" height="80"></canvas>

                        <div class="panel-label">hold</div>
                        <canvas id="hold-canvas" width="80" height="80"></canvas>
                    </div>
                    <button id="start-btn">START</button>
                    <div id="msg">← → déplacer<br>↑ pivoter<br>↓ descendre<br>Espace : drop <br> P : pause <br> SHIFT : hold</div>
                </div>
            </div>
        </div>