const canvas = document.getElementById('gameCanvas');
const ctx = canvas.getContext('2d');
const scoreBoard = document.getElementById('score-board');
const socket = io('http://localhost:3000');

const BLOCK_SIZE = 40;
const COLORS = {
    fence: '#4a2a0a',
    player: '#00FF00',
    agent: '#00ccff', // Cor para o Agente IA
    block: '#FF0000',
    background: '#1a1a1a'
};

function draw(gameState) {
    ctx.fillStyle = COLORS.background;
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    ctx.fillStyle = COLORS.fence;
    for (let i = 0; i < canvas.width / BLOCK_SIZE; i++) {
        ctx.fillRect(i * BLOCK_SIZE, 0, BLOCK_SIZE, BLOCK_SIZE);
        ctx.fillRect(i * BLOCK_SIZE, canvas.height - BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
        ctx.fillRect(0, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
        ctx.fillRect(canvas.width - BLOCK_SIZE, i * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
    }
    
    // Desenha todos os jogadores
    scoreBoard.innerHTML = '';
    for (const id in gameState.players) {
        const player = gameState.players[id];
        const isAgent = id === 'ai_agent_masp';
        ctx.fillStyle = isAgent ? COLORS.agent : COLORS.player;
        ctx.fillRect(player.pos[0] * BLOCK_SIZE, player.pos[1] * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE);
        
        // Atualiza placar
        const scoreSpan = document.createElement('span');
        scoreSpan.textContent = `${isAgent ? '🤖 Agente' : 'Você'}: ${player.score}`;
        scoreSpan.style.color = isAgent ? COLORS.agent : COLORS.player;
        scoreBoard.appendChild(scoreSpan);
    }

    ctx.fillStyle = COLORS.block;
    ctx.fillRect(gameState.block_pos[0], gameState.block_pos[1], BLOCK_SIZE, BLOCK_SIZE);
}

socket.on('update_state', (gameState) => {
    draw(gameState);
});

window.addEventListener('keydown', (e) => {
    let direction = null;
    switch (e.key) {
        case 'ArrowUp': direction = 'up'; break;
        case 'ArrowDown': direction = 'down'; break;
        case 'ArrowLeft': direction = 'left'; break;
        case 'ArrowRight': direction = 'right'; break;
    }
    if (direction) {
        e.preventDefault();
        socket.emit('mover', { direcao: direction });
    }
});