/**
 * Cliente do jogo em tempo real
 * Gerencia a interface do usuário e comunicação com o servidor
 */

class GameClient {
    constructor() {
        this.canvas = document.getElementById('gameCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.scoreBoard = document.getElementById('score-board');
        this.socket = io('http://localhost:3000');
        
        this.BLOCK_SIZE = 40;
        this.COLORS = {
            fence: '#4a2a0a',
            player: '#00FF00',
            agent: '#00ccff',
            block: '#FF0000',
            background: '#1a1a1a',
            text: '#ffffff'
        };
        
        this.gameState = null;
        this.isConnected = false;
        
        this.init();
    }
    
    init() {
        this.setupSocketHandlers();
        this.setupEventListeners();
        this.showConnectionStatus('🔄 Conectando...', '#ffaa00');
    }
    
    setupSocketHandlers() {
        // Conexão estabelecida
        this.socket.on('connect', () => {
            this.isConnected = true;
            this.showConnectionStatus('✅ Conectado', '#00ff00');
            console.log('🔗 Conectado ao servidor de jogo');
        });
        
        // Desconexão
        this.socket.on('disconnect', () => {
            this.isConnected = false;
            this.showConnectionStatus('❌ Desconectado', '#ff0000');
            console.log('🔌 Desconectado do servidor de jogo');
        });
        
        // Atualização do estado do jogo
        this.socket.on('update_state', (gameState) => {
            this.gameState = gameState;
            this.draw();
        });
        
        // Confirmação de implantação de estratégia
        this.socket.on('strategy_deployed', (data) => {
            if (data.status === 'success') {
                this.showNotification('🤖 Estratégia da IA implantada com sucesso!', 'success');
            } else {
                this.showNotification(`❌ Falha ao implantar estratégia: ${data.error}`, 'error');
            }
        });
        
        // Estatísticas do jogo
        this.socket.on('game_stats', (stats) => {
            this.updateStats(stats);
        });
        
        // Erro de conexão
        this.socket.on('connect_error', (error) => {
            this.showConnectionStatus('❌ Erro de conexão', '#ff0000');
            console.error('❌ Erro de conexão:', error);
        });
    }
    
    setupEventListeners() {
        // Controles de teclado
        window.addEventListener('keydown', (e) => {
            if (!this.isConnected) return;
            
            let direction = null;
            switch (e.key) {
                case 'ArrowUp': direction = 'up'; break;
                case 'ArrowDown': direction = 'down'; break;
                case 'ArrowLeft': direction = 'left'; break;
                case 'ArrowRight': direction = 'right'; break;
            }
            
            if (direction) {
                e.preventDefault();
                this.socket.emit('mover', { direcao: direction });
            }
        });
        
        // Solicitar estatísticas periodicamente
        setInterval(() => {
            if (this.isConnected) {
                this.socket.emit('get_stats');
            }
        }, 5000);
    }
    
    draw() {
        if (!this.gameState) return;
        
        // Limpa o canvas
        this.ctx.fillStyle = this.COLORS.background;
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // Desenha as paredes
        this.drawWalls();
        
        // Desenha os jogadores
        this.drawPlayers();
        
        // Desenha o bloco de recompensa
        this.drawReward();
        
        // Atualiza o placar
        this.updateScoreBoard();
    }
    
    drawWalls() {
        this.ctx.fillStyle = this.COLORS.fence;
        for (let i = 0; i < this.canvas.width / this.BLOCK_SIZE; i++) {
            // Paredes horizontais
            this.ctx.fillRect(i * this.BLOCK_SIZE, 0, this.BLOCK_SIZE, this.BLOCK_SIZE);
            this.ctx.fillRect(i * this.BLOCK_SIZE, this.canvas.height - this.BLOCK_SIZE, this.BLOCK_SIZE, this.BLOCK_SIZE);
            
            // Paredes verticais
            this.ctx.fillRect(0, i * this.BLOCK_SIZE, this.BLOCK_SIZE, this.BLOCK_SIZE);
            this.ctx.fillRect(this.canvas.width - this.BLOCK_SIZE, i * this.BLOCK_SIZE, this.BLOCK_SIZE, this.BLOCK_SIZE);
        }
    }
    
    drawPlayers() {
        this.scoreBoard.innerHTML = '';
        
        for (const id in this.gameState.players) {
            const player = this.gameState.players[id];
            const isAgent = id === 'ai_agent_masp';
            
            // Desenha o jogador
            this.ctx.fillStyle = isAgent ? this.COLORS.agent : this.COLORS.player;
            this.ctx.fillRect(
                player.pos[0] * this.BLOCK_SIZE, 
                player.pos[1] * this.BLOCK_SIZE, 
                this.BLOCK_SIZE, 
                this.BLOCK_SIZE
            );
            
            // Adiciona borda para melhor visibilidade
            this.ctx.strokeStyle = this.COLORS.text;
            this.ctx.lineWidth = 2;
            this.ctx.strokeRect(
                player.pos[0] * this.BLOCK_SIZE, 
                player.pos[1] * this.BLOCK_SIZE, 
                this.BLOCK_SIZE, 
                this.BLOCK_SIZE
            );
            
            // Atualiza o placar
            this.addScoreToBoard(isAgent ? '🤖 Agente' : '👤 Você', player.score, isAgent ? this.COLORS.agent : this.COLORS.player);
        }
    }
    
    drawReward() {
        this.ctx.fillStyle = this.COLORS.block;
        this.ctx.fillRect(
            this.gameState.block_pos[0], 
            this.gameState.block_pos[1], 
            this.BLOCK_SIZE, 
            this.BLOCK_SIZE
        );
        
        // Adiciona brilho ao bloco de recompensa
        this.ctx.fillStyle = 'rgba(255, 255, 255, 0.3)';
        this.ctx.fillRect(
            this.gameState.block_pos[0] + 2, 
            this.gameState.block_pos[1] + 2, 
            this.BLOCK_SIZE - 4, 
            this.BLOCK_SIZE - 4
        );
    }
    
    updateScoreBoard() {
        // O placar já foi atualizado em drawPlayers()
    }
    
    addScoreToBoard(name, score, color) {
        const scoreSpan = document.createElement('span');
        scoreSpan.textContent = `${name}: ${score}`;
        scoreSpan.style.color = color;
        scoreSpan.style.fontWeight = 'bold';
        scoreSpan.style.margin = '0 10px';
        scoreSpan.style.textShadow = '1px 1px 2px black';
        this.scoreBoard.appendChild(scoreSpan);
    }
    
    showConnectionStatus(message, color) {
        // Cria ou atualiza o indicador de status
        let statusIndicator = document.getElementById('connection-status');
        if (!statusIndicator) {
            statusIndicator = document.createElement('div');
            statusIndicator.id = 'connection-status';
            statusIndicator.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 8px 15px;
                border-radius: 25px;
                color: white;
                font-weight: bold;
                z-index: 1000;
                font-size: 0.9rem;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
                transition: all 0.3s ease;
            `;
            document.body.appendChild(statusIndicator);
        }
        
        statusIndicator.textContent = message;
        statusIndicator.style.backgroundColor = color;
    }
    
    showNotification(message, type) {
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            padding: 15px 20px;
            border-radius: 8px;
            color: white;
            font-weight: bold;
            z-index: 1001;
            background-color: ${type === 'success' ? '#4CAF50' : '#f44336'};
            box-shadow: 0 4px 8px rgba(0,0,0,0.3);
        `;
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        // Remove a notificação após 3 segundos
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 3000);
    }
    
    updateStats(stats) {
        // Atualiza estatísticas se necessário
        console.log('📊 Estatísticas do jogo:', stats);
    }
}

// Inicializa o cliente do jogo quando a página carregar
document.addEventListener('DOMContentLoaded', () => {
    new GameClient();
});