@echo off
chcp 65001 >nul
REM Script de inicialização do Agent Architect (MASP) para Windows
REM Este script inicia todos os componentes do sistema MASP

echo.
echo ========================================
echo 🚀 Agent Architect (MASP) - Windows
echo ========================================
echo.

REM Verifica se Python está instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado no PATH
    echo 💡 Instale Python 3.8+ e adicione ao PATH
    pause
    exit /b 1
)

REM Verifica se Node.js está instalado
node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js não encontrado no PATH
    echo 💡 Instale Node.js e adicione ao PATH
    pause
    exit /b 1
)

echo ✅ Python e Node.js encontrados
echo.

REM Verifica se o arquivo .env existe
if not exist "masp_agent\.env" (
    echo ⚠️ Arquivo .env não encontrado
    echo 📝 Criando arquivo .env de exemplo...
    copy "masp_agent\env.example" "masp_agent\.env" >nul 2>&1
    echo 💡 Configure sua chave de API do Gemini no arquivo masp_agent\.env
    echo.
)

REM Instala dependências Python se necessário
echo 📦 Verificando dependências Python...
cd masp_agent
if not exist "venv" (
    echo 🔧 Criando ambiente virtual...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt >nul 2>&1
cd ..

REM Instala dependências Node.js se necessário
echo 📦 Verificando dependências Node.js...
cd realtime_game
if not exist "node_modules" (
    echo 🔧 Instalando dependências...
    npm install >nul 2>&1
)
cd ..

echo ✅ Dependências verificadas
echo.

REM Inicia o servidor MCP (Oracle)
echo 🔮 Iniciando servidor MCP (Oracle)...
start "MCP Server" cmd /k "cd mcp_server && python mcp_game_instance.py"

REM Aguarda um pouco para o servidor MCP inicializar
timeout /t 3 /nobreak >nul

REM Inicia o servidor de jogo (Board)
echo 🎮 Iniciando servidor de jogo (Board)...
start "Game Server" cmd /k "cd realtime_game && node server.js"

REM Aguarda um pouco para o servidor de jogo inicializar
timeout /t 3 /nobreak >nul

REM Inicia o agente MASP (Brain)
echo 🧠 Iniciando agente MASP (Brain)...
start "MASP Agent" cmd /k "cd masp_agent && venv\Scripts\activate.bat && python agent_masp.py"

echo.
echo ========================================
echo 🎉 Todos os componentes iniciados!
echo ========================================
echo.
echo 📱 Acesse o jogo em: http://localhost:3000
echo 🔮 API MCP em: http://127.0.0.1:8000
echo 🧠 Agente MASP rodando em background
echo.
echo 💡 Pressione qualquer tecla para abrir o jogo no navegador...
pause >nul

REM Abre o navegador
start http://localhost:3000

echo.
echo 🎮 Jogo aberto no navegador!
echo 🛑 Para parar todos os serviços, feche as janelas dos terminais
echo.
pause 