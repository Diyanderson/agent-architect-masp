/**
 * Servidor de Jogo em Tempo Real (Plataforma e Sistema)
 * Este é o "Tabuleiro" onde o jogo acontece e onde a IA é implantada.
 */

const express = require('express');
const http = require('http');
const { Server } = require("socket.io");
const path = require('path');
const GameManager = require('./game_manager');

// Configurações do servidor
const PORT = process.env.PORT || 3000;
const FPS = 10;

// Inicialização do servidor
const app = express();
const server = http.createServer(app);
const io = new Server(server, { 
    cors: { 
        origin: "*",
        methods: ["GET", "POST"]
    } 
});

// Serve arquivos estáticos
app.use(express.static(path.join(__dirname, 'public')));

// Inicializa o gerenciador do jogo
const gameManager = new GameManager();

// Loop principal do jogo
const gameLoop = setInterval(() => {
    try {
        // Executa a estratégia da IA se disponível
        gameManager.executeAIStrategy();
        
        // Atualiza o estado do jogo
        gameManager.update();
        
        // Envia o estado atualizado para todos os clientes
        io.emit('update_state', gameManager.getState());
        
    } catch (error) {
        console.error("❌ Erro no loop do jogo:", error);
    }
}, 1000 / FPS);

// Gerenciamento de conexões Socket.IO
io.on('connection', (socket) => {
    console.log(`➕ Cliente conectado: ${socket.id}`);
    
    // Adiciona o jogador ao jogo
    gameManager.addPlayer(socket.id);
    io.emit('update_state', gameManager.getState());

    // Handler para movimentos do jogador
    socket.on('mover', (data) => {
        if (gameManager.movePlayer(socket.id, data.direcao)) {
            console.log(`🎮 Jogador ${socket.id} moveu para ${data.direcao}`);
            io.emit('update_state', gameManager.getState());
        } else {
            console.log(`❌ Movimento inválido: ${data.direcao} por ${socket.id}`);
        }
    });

    // Handler para implantação de estratégia da IA
    socket.on('deploy_strategy', (data) => {
        console.log('🤖 Nova estratégia recebida do socket:', socket.id);
        
        const result = gameManager.deployAIStrategy(data.code, socket.id);
        socket.emit('strategy_deployed', result);
        
        if (result.status === 'success') {
            console.log('✅ Estratégia implantada com sucesso!');
            io.emit('update_state', gameManager.getState());
        } else {
            console.log('❌ Falha ao implantar estratégia:', result.error);
        }
    });

    // Handler para desconexão
    socket.on('disconnect', () => {
        console.log(`➖ Cliente desconectado: ${socket.id}`);
        
        // Se era o agente IA, limpa a estratégia
        if (socket.id === gameManager.aiAgentSocketId) {
            console.log('🤖 Agente MASP desconectado.');
            gameManager.clearAIStrategy();
        } else {
            gameManager.removePlayer(socket.id);
        }
        
        io.emit('update_state', gameManager.getState());
    });

    // Handler para solicitar estatísticas
    socket.on('get_stats', () => {
        const stats = gameManager.getStats();
        console.log('📊 Estatísticas solicitadas:', stats);
        socket.emit('game_stats', stats);
    });
});

// Rota de status da API
app.get('/api/status', (req, res) => {
    const status = {
        status: 'running',
        timestamp: new Date().toISOString(),
        stats: gameManager.getStats(),
        uptime: process.uptime(),
        memory: process.memoryUsage()
    };
    
    console.log('📊 Status da API solicitado');
    res.json(status);
});

// Rota de saúde
app.get('/health', (req, res) => {
    console.log('❤️ Health check solicitado');
    res.json({ 
        status: 'healthy',
        timestamp: new Date().toISOString(),
        uptime: process.uptime()
    });
});

// Inicialização do servidor
server.listen(PORT, () => {
    console.log(`🎮 Real-Time Game Server rodando em http://localhost:${PORT}`);
    console.log(`📊 API Status: http://localhost:${PORT}/api/status`);
    console.log(`❤️ Health Check: http://localhost:${PORT}/health`);
    console.log(`🛑 Pressione Ctrl+C para parar.`);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\n🛑 Encerrando servidor...');
    clearInterval(gameLoop);
    server.close(() => {
        console.log('✅ Servidor encerrado com sucesso.');
        process.exit(0);
    });
});

process.on('SIGTERM', () => {
    console.log('\n🛑 Servidor recebeu sinal de término...');
    clearInterval(gameLoop);
    server.close(() => {
        console.log('✅ Servidor encerrado com sucesso.');
        process.exit(0);
    });
});

// Tratamento de erros não capturados
process.on('uncaughtException', (error) => {
    console.error('🔥 Erro não capturado:', error);
    process.exit(1);
});

process.on('unhandledRejection', (reason, promise) => {
    console.error('🔥 Promise rejeitada não tratada:', reason);
    process.exit(1);
});