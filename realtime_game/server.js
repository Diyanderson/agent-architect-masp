const express = require('express');
const http = require('http');
const { Server } = require("socket.io");
const path = require('path');

const app = express();
const server = http.createServer(app);
const io = new Server(server, { cors: { origin: "*" } });

// Serve os arquivos do cliente (index.html, etc.)
app.use(express.static(path.join(__dirname, 'public')));

// Constantes do Jogo
const WIDTH = 400, HEIGHT = 400, BLOCK_SIZE = 40, FPS = 10;
const DIRECTIONS = { 'up': [0, -1], 'down': [0, 1], 'left': [-1, 0], 'right': [1, 0] };

// Classe que gerencia o estado do jogo
class Game {
    constructor() {
        this.players = {}; // Suporta múltiplos jogadores (humanos e IAs)
        this.rows = HEIGHT / BLOCK_SIZE;
        this.cols = WIDTH / BLOCK_SIZE;
        this.block_pos = this.randomBlock();
    }
    
    addPlayer(id) {
        this.players[id] = { pos: this.centerPos(), score: 0, id: id };
        console.log(`Player ${id} adicionado.`);
    }

    removePlayer(id) {
        if (this.players[id]) {
            delete this.players[id];
            console.log(`Player ${id} removido.`);
        }
    }

    centerPos() { return [Math.floor(this.cols / 2), Math.floor(this.rows / 2)]; }
    
    randomBlock() {
        let x, y;
        do {
            x = Math.floor(Math.random() * (this.cols - 2)) + 1;
            y = Math.floor(Math.random() * (this.rows - 2)) + 1;
        } while (this.players && Object.values(this.players).some(p => p.pos[0] === x && p.pos[1] === y));
        return [x, y];
    }

    movePlayer(playerId, direction) {
        if (!this.players[playerId] || !(direction in DIRECTIONS)) return false;
        
        const [dx, dy] = DIRECTIONS[direction];
        const player = this.players[playerId];
        const new_x = player.pos[0] + dx;
        const new_y = player.pos[1] + dy;
        
        if (new_x > 0 && new_x < this.cols - 1 && new_y > 0 && new_y < this.rows - 1) {
            player.pos = [new_x, new_y];
            return true;
        }
        return false;
    }

    update() {
        for (const playerId in this.players) {
            const player = this.players[playerId];
            if (player.pos[0] === this.block_pos[0] && player.pos[1] === this.block_pos[1]) {
                player.score++;
                this.block_pos = this.randomBlock();
                console.log(`Player ${playerId} pontuou! Score: ${player.score}`);
            }
        }
    }
    
    getState() {
        return {
            players: this.players,
            block_pos: [this.block_pos[0] * BLOCK_SIZE, this.block_pos[1] * BLOCK_SIZE],
        };
    }
}

const game = new Game();
let aiStrategyFunction = null; // Armazena a função gerada pela IA
let aiAgentSocketId = null;    // Armazena o ID do socket do agente

// Loop do jogo
setInterval(() => {
    // Se a IA implantou uma estratégia, ela joga
    if (aiStrategyFunction && game.players['ai_agent_masp']) {
        const aiPlayer = game.players['ai_agent_masp'];
        const move = aiStrategyFunction({ x: aiPlayer.pos[0], y: aiPlayer.pos[1] }, { x: game.block_pos[0], y: game.block_pos[1] });
        if (move) {
            game.movePlayer('ai_agent_masp', move);
        }
    }
    game.update(); 
    io.emit('update_state', game.getState());
}, 1000 / FPS);


io.on('connection', (socket) => {
    console.log(`➕ Cliente conectado: ${socket.id}`);
    game.addPlayer(socket.id);
    io.emit('update_state', game.getState());

    socket.on('mover', (data) => {
        if (game.movePlayer(socket.id, data.direcao)) {
            io.emit('update_state', game.getState());
        }
    });

    socket.on('deploy_strategy', (data) => {
        console.log('🤖 Nova estratégia recebida do socket:', socket.id);
        
        game.removePlayer(socket.id);
        
        if (aiAgentSocketId && game.players['ai_agent_masp']) {
            game.removePlayer('ai_agent_masp');
            console.log('🤖 Removendo agente antigo.');
        }

        try {
            aiStrategyFunction = new Function('playerPos', 'rewardPos', `
                const { x: px, y: py } = playerPos;
                const { x: rx, y: ry } = rewardPos;
                ${data.code}
            `);
            game.addPlayer('ai_agent_masp');
            aiAgentSocketId = socket.id;
            console.log(`✅ Estratégia implantada. Agente MASP (${aiAgentSocketId}) está ativo.`);
            socket.emit('strategy_deployed', { status: 'success' });
        } catch (e) {
            console.error("❌ Erro ao compilar estratégia:", e);
            socket.emit('strategy_deployed', { status: 'failed', error: e.message });
        }
    });

    socket.on('disconnect', () => {
        console.log(`➖ Cliente desconectado: ${socket.id}`);
        if (socket.id === aiAgentSocketId) {
            console.log('🤖 Agente MASP desconectado.');
            game.removePlayer('ai_agent_masp');
            aiStrategyFunction = null;
            aiAgentSocketId = null;
        } else {
            game.removePlayer(socket.id);
        }
        io.emit('update_state', game.getState());
    });
});

const PORT = 3000;
server.listen(PORT, () => {
    console.log(`🎮 Real-Time Game Server rodando em http://localhost:${PORT}`);
});