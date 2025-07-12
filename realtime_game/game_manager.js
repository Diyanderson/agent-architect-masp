/**
 * Gerenciador do jogo em tempo real
 * Responsável por gerenciar o estado do jogo, jogadores e IA
 */

// Constantes do Jogo
const WIDTH = 400, HEIGHT = 400, BLOCK_SIZE = 40, FPS = 10;
const DIRECTIONS = { 
    'up': [0, -1], 
    'down': [0, 1], 
    'left': [-1, 0], 
    'right': [1, 0] 
};

class GameManager {
    constructor() {
        this.players = {}; // Suporta múltiplos jogadores (humanos e IAs)
        this.rows = HEIGHT / BLOCK_SIZE;
        this.cols = WIDTH / BLOCK_SIZE;
        this.block_pos = this.randomBlock();
        this.aiStrategyFunction = null;
        this.aiAgentSocketId = null;
    }
    
    /**
     * Adiciona um novo jogador ao jogo
     * @param {string} id - ID único do jogador
     */
    addPlayer(id) {
        this.players[id] = { 
            pos: this.centerPos(), 
            score: 0, 
            id: id,
            isAgent: id === 'ai_agent_masp'
        };
        console.log(`👤 Player ${id} adicionado.`);
    }

    /**
     * Remove um jogador do jogo
     * @param {string} id - ID do jogador a ser removido
     */
    removePlayer(id) {
        if (this.players[id]) {
            delete this.players[id];
            console.log(`👋 Player ${id} removido.`);
        }
    }

    /**
     * Retorna a posição central do tabuleiro
     * @returns {Array} [x, y] da posição central
     */
    centerPos() { 
        return [Math.floor(this.cols / 2), Math.floor(this.rows / 2)]; 
    }
    
    /**
     * Gera uma posição aleatória para o bloco de recompensa
     * @returns {Array} [x, y] da posição do bloco
     */
    randomBlock() {
        let x, y;
        do {
            x = Math.floor(Math.random() * (this.cols - 2)) + 1;
            y = Math.floor(Math.random() * (this.rows - 2)) + 1;
        } while (this.players && Object.values(this.players).some(p => p.pos[0] === x && p.pos[1] === y));
        return [x, y];
    }

    /**
     * Move um jogador na direção especificada
     * @param {string} playerId - ID do jogador
     * @param {string} direction - Direção do movimento
     * @returns {boolean} True se o movimento foi válido
     */
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

    /**
     * Atualiza o estado do jogo (colisões, pontuação, etc.)
     */
    update() {
        for (const playerId in this.players) {
            const player = this.players[playerId];
            if (player.pos[0] === this.block_pos[0] && player.pos[1] === this.block_pos[1]) {
                player.score++;
                this.block_pos = this.randomBlock();
                const playerType = player.isAgent ? '🤖 Agente' : '👤 Jogador';
                console.log(`🏆 ${playerType} ${playerId} pontuou! Score: ${player.score}`);
            }
        }
    }
    
    /**
     * Retorna o estado atual do jogo
     * @returns {Object} Estado do jogo
     */
    getState() {
        return {
            players: this.players,
            block_pos: [this.block_pos[0] * BLOCK_SIZE, this.block_pos[1] * BLOCK_SIZE],
        };
    }

    /**
     * Executa a estratégia da IA se disponível
     */
    executeAIStrategy() {
        if (this.aiStrategyFunction && this.players['ai_agent_masp']) {
            const aiPlayer = this.players['ai_agent_masp'];
            try {
                const move = this.aiStrategyFunction(
                    { x: aiPlayer.pos[0], y: aiPlayer.pos[1] }, 
                    { x: this.block_pos[0], y: this.block_pos[1] }
                );
                if (move) {
                    this.movePlayer('ai_agent_masp', move);
                }
            } catch (error) {
                console.error("❌ Erro ao executar estratégia da IA:", error);
            }
        }
    }

    /**
     * Implanta uma nova estratégia para a IA
     * @param {string} jsCode - Código JavaScript da estratégia
     * @param {string} socketId - ID do socket que enviou a estratégia
     * @returns {Object} Resultado da implantação
     */
    deployAIStrategy(jsCode, socketId) {
        console.log('🤖 Nova estratégia recebida do socket:', socketId);
        
        // Remove o socket que enviou a estratégia
        this.removePlayer(socketId);
        
        // Remove agente antigo se existir
        if (this.aiAgentSocketId && this.players['ai_agent_masp']) {
            this.removePlayer('ai_agent_masp');
            console.log('🔄 Removendo agente antigo.');
        }

        try {
            // Cria a função da estratégia
            this.aiStrategyFunction = new Function('playerPos', 'rewardPos', `
                const { x: px, y: py } = playerPos;
                const { x: rx, y: ry } = rewardPos;
                ${jsCode}
            `);
            
            // Adiciona o agente IA
            this.addPlayer('ai_agent_masp');
            this.aiAgentSocketId = socketId;
            
            console.log(`✅ Estratégia implantada. Agente MASP (${aiAgentSocketId}) está ativo.`);
            return { status: 'success' };
            
        } catch (error) {
            console.error("❌ Erro ao compilar estratégia:", error);
            return { status: 'failed', error: error.message };
        }
    }

    /**
     * Limpa a estratégia da IA
     */
    clearAIStrategy() {
        this.aiStrategyFunction = null;
        this.aiAgentSocketId = null;
        if (this.players['ai_agent_masp']) {
            this.removePlayer('ai_agent_masp');
        }
        console.log('🧹 Estratégia da IA limpa.');
    }

    /**
     * Retorna estatísticas do jogo
     * @returns {Object} Estatísticas
     */
    getStats() {
        const humanPlayers = Object.values(this.players).filter(p => !p.isAgent);
        const aiPlayers = Object.values(this.players).filter(p => p.isAgent);
        
        return {
            totalPlayers: Object.keys(this.players).length,
            humanPlayers: humanPlayers.length,
            aiPlayers: aiPlayers.length,
            hasAIStrategy: this.aiStrategyFunction !== null,
            blockPosition: this.block_pos,
            timestamp: new Date().toISOString()
        };
    }
}

module.exports = GameManager; 