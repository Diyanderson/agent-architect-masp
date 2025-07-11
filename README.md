# Agent Architect (MASP)

Este projeto demonstra a arquitetura MASP (Modelo-Agente-Sistema-Plataforma) para criar um agente de IA autônomo que aprende as regras de um jogo e desenvolve sua própria estratégia para jogá-lo em tempo real.

## Arquitetura

O projeto é dividido em três componentes principais, cada um representando uma parte da arquitetura MASP:

1.  **O Oráculo (`mcp_server`)**: Este é o **Modelo** do nosso sistema. Ele expõe as regras e a mecânica do jogo através de uma API de ferramentas (usando FastMCP). O agente consulta este servidor para "aprender" como o jogo funciona.

2.  **O Tabuleiro (`realtime_game`)**: Esta é a **Plataforma** e o **Sistema**. É um ambiente de jogo interativo e em tempo real onde tanto um jogador humano quanto o agente de IA podem atuar. Ele consiste em um servidor Node.js com WebSockets e um cliente web simples.

3.  **O Cérebro (`masp_agent`)**: Este é o **Agente**. É um script Python que:
    *   Consulta o Oráculo para entender as regras do jogo.
    *   Usa um modelo de linguagem generativo (Google Gemini) para analisar as regras e criar uma estratégia de jogo.
    *   Gera o código da estratégia em JavaScript.
    *   Implanta a estratégia no Tabuleiro para que o agente possa jogar.

## Como Funciona

1.  **Aprendizado**: O `masp_agent` envia uma requisição para o `mcp_server` para obter a lista de "ferramentas" (ações possíveis no jogo).
2.  **Raciocínio**: O agente constrói um prompt detalhado para a API Gemini, explicando o objetivo do jogo e as ferramentas disponíveis. Ele pede à IA para criar uma função JavaScript que represente uma estratégia de jogo.
3.  **Implantação**: O agente recebe o código JavaScript gerado pelo Gemini e o envia para o `realtime_game` server via WebSocket.
4.  **Ação**: O servidor do jogo compila e executa a função de estratégia recebida, permitindo que o agente de IA jogue de forma autônoma, movendo-se no tabuleiro para coletar recompensas.

## Como Executar o Projeto

### Pré-requisitos

*   Python 3.8+
*   Node.js 14+
*   Uma chave de API do Google Gemini.

### 1. Configuração do Agente (Cérebro)

Primeiro, configure o agente que usará a IA.

```bash
# Navegue até a pasta do agente
cd masp_agent

# Crie um ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Configure sua chave de API
# Renomeie o arquivo .env.example para .env
# Abra o .env e cole sua chave da API do Google Gemini
GEMINI_API_KEY="SUA_CHAVE_DE_API_AQUI"
```

### 2. Iniciando o Oráculo (Servidor de Regras)

Em um **novo terminal**, inicie o servidor que define as regras do jogo.

```bash
# Navegue até a pasta do servidor MCP
cd mcp_server

# Crie e ative um ambiente virtual
python -m venv venv
source venv/bin/activate # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Inicie o servidor
python mcp_game_instance.py
```

Você verá a mensagem: `🚀 Servidor MCP (Oráculo de Regras) rodando em http://127.0.0.1:8000`

### 3. Iniciando o Tabuleiro (Servidor do Jogo)

Em um **terceiro terminal**, inicie o servidor do jogo em tempo real.

```bash
# Navegue até a pasta do jogo
cd realtime_game

# Instale as dependências do Node.js
npm install

# Inicie o servidor
npm start
```

Você verá a mensagem: `🎮 Real-Time Game Server rodando em http://localhost:3000`

### 4. Executando o Agente (Cérebro)

Agora, volte para o **primeiro terminal** (onde você configurou o `masp_agent`) e execute o agente.

```bash
# Certifique-se de que você está na pasta masp_agent e o ambiente virtual está ativado
python agent_masp.py
```

O agente irá se conectar aos outros dois servidores, aprender as regras, gerar uma estratégia e implantá-la. 

### 5. Visualizando o Jogo

Abra seu navegador e acesse:

**http://localhost:3000**

Você verá dois jogadores:
*   **Você (Verde)**: Controlado pelas setas do teclado.
*   **🤖 Agente (Azul)**: Controlado pela IA que você acabou de implantar.

Ambos competirão para coletar os blocos vermelhos.
