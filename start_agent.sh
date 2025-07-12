#!/bin/bash

# Script de inicialização do Agent Architect (MASP) para Linux/Mac
# Este script inicia todos os componentes do sistema MASP

echo ""
echo "========================================"
echo "🚀 Agent Architect (MASP) - Linux/Mac"
echo "========================================"
echo ""

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado no PATH"
    echo "💡 Instale Python 3.8+ e adicione ao PATH"
    exit 1
fi

# Verifica se Node.js está instalado
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado no PATH"
    echo "💡 Instale Node.js e adicione ao PATH"
    exit 1
fi

echo "✅ Python3 e Node.js encontrados"
echo ""

# Verifica se o arquivo .env existe
if [ ! -f "masp_agent/.env" ]; then
    echo "⚠️ Arquivo .env não encontrado"
    echo "📝 Criando arquivo .env de exemplo..."
    cp "masp_agent/env.example" "masp_agent/.env" 2>/dev/null || echo "💡 Crie o arquivo masp_agent/.env manualmente"
    echo "💡 Configure sua chave de API do Gemini no arquivo masp_agent/.env"
    echo ""
fi

# Instala dependências Python se necessário
echo "📦 Verificando dependências Python..."
cd masp_agent
if [ ! -d "venv" ]; then
    echo "🔧 Criando ambiente virtual..."
    python3 -m venv venv
fi
source venv/bin/activate
pip install -r requirements.txt >/dev/null 2>&1
cd ..

# Instala dependências Node.js se necessário
echo "📦 Verificando dependências Node.js..."
cd realtime_game
if [ ! -d "node_modules" ]; then
    echo "🔧 Instalando dependências..."
    npm install >/dev/null 2>&1
fi
cd ..

echo "✅ Dependências verificadas"
echo ""

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "🛑 Encerrando todos os processos..."
    pkill -f "mcp_game_instance.py" 2>/dev/null
    pkill -f "server.js" 2>/dev/null
    pkill -f "agent_masp.py" 2>/dev/null
    echo "✅ Processos encerrados"
    exit 0
}

# Captura Ctrl+C para limpeza
trap cleanup SIGINT

# Inicia o servidor MCP (Oracle)
echo "🔮 Iniciando servidor MCP (Oracle)..."
cd mcp_server
python3 mcp_game_instance.py &
MCP_PID=$!
cd ..

# Aguarda um pouco para o servidor MCP inicializar
sleep 3

# Inicia o servidor de jogo (Board)
echo "🎮 Iniciando servidor de jogo (Board)..."
cd realtime_game
node server.js &
GAME_PID=$!
cd ..

# Aguarda um pouco para o servidor de jogo inicializar
sleep 3

# Inicia o agente MASP (Brain)
echo "🧠 Iniciando agente MASP (Brain)..."
cd masp_agent
source venv/bin/activate
python3 agent_masp.py &
AGENT_PID=$!
cd ..

echo ""
echo "========================================"
echo "🎉 Todos os componentes iniciados!"
echo "========================================"
echo ""
echo "📱 Acesse o jogo em: http://localhost:3000"
echo "🔮 API MCP em: http://127.0.0.1:8000"
echo "🧠 Agente MASP rodando em background"
echo ""
echo "💡 Pressione Ctrl+C para parar todos os serviços"
echo ""

# Aguarda um pouco e abre o navegador
sleep 2
if command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open http://localhost:3000 &
elif command -v open &> /dev/null; then
    # macOS
    open http://localhost:3000 &
fi

echo "🎮 Jogo aberto no navegador!"
echo ""

# Aguarda indefinidamente
while true; do
    sleep 1
done 