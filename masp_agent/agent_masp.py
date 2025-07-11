'''
import os
import google.generativeai as genai
import requests
import socketio
import time
from dotenv import load_dotenv

# --- Configuração ---
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MCP_SERVER_URL = "http://127.0.0.1:8000"
REALTIME_GAME_URL = "http://localhost:3000"
AGENT_ID = "ai_agent_masp"

# --- Conexão com o Servidor de Jogo (Tabuleiro) ---
sio = socketio.Client()

@sio.event
def connect():
    print("🤖 Agente conectado ao servidor de jogo.")
    # Após conectar, o agente inicia o processo de aprendizado e implantação.
    learn_rules_and_deploy_strategy()

@sio.event
def disconnect():
    print("🤖 Agente desconectado do servidor de jogo.")

@sio.event
def strategy_deployed(data):
    if data['status'] == 'success':
        print("✅ Estratégia implantada com sucesso no servidor de jogo!")
    else:
        print(f"❌ Falha ao implantar estratégia: {data.get('error', 'Erro desconhecido')}")
    # Desconecta após a tentativa de implantação para não deixar a conexão pendurada.
    sio.disconnect()

# --- Função Principal do Agente ---
def learn_rules_and_deploy_strategy():
    """
    O coração do agente MASP.
    1. Conecta-se ao Oráculo (MCP Server) para obter as regras.
    2. Constrói um prompt para o Gemini com base nas regras.
    3. Pede ao Gemini para gerar uma estratégia de jogo em JavaScript.
    4. Implanta a estratégia no Tabuleiro (Real-time Game Server).
    """
    try:
        # 1. Obter as regras do Oráculo (MCP Server)
        print("🧠 Tentando aprender as regras do jogo no Oráculo MCP...")
        response = requests.get(f"{MCP_SERVER_URL}/tools")
        response.raise_for_status()
        game_tools = response.json()
        
        tools_description = "
".join([
            f"- `{tool['name']}({', '.join(tool['args'])})`: {tool['description']}"
            for tool in game_tools
        ])
        print("📚 Regras aprendidas com sucesso!")

        # 2. Construir o prompt para o Gemini
        prompt = f"""
        Você é um agente de IA especialista em programação e jogos. Sua tarefa é criar uma estratégia para um jogo simples.

        **Objetivo do Jogo:**
        O jogador ('P') deve coletar a recompensa ('R') em um mapa cercado por paredes ('#').

        **Regras e Ferramentas Disponíveis (via API):**
        {tools_description}
        O mapa tem coordenadas onde (0,0) é o canto superior esquerdo.

        **Sua Tarefa:**
        Crie uma função JavaScript que receba a posição do jogador `playerPos` (um objeto com `x` e `y`) e a posição da recompensa `rewardPos` (também com `x` e `y`) e retorne a próxima melhor direção para o jogador se mover.
        As direções de retorno possíveis são: "up", "down", "left", "right".

        **Exemplo de Estratégia (Simples):**
        Se a recompensa está à direita do jogador (rx > px), a função deve retornar "right".

        **Requisitos da Estratégia:**
        - A lógica deve ser contida em uma única função.
        - A função deve ser eficiente e direta.
        - A estratégia deve ser inteligente: mova-se na direção horizontal e depois na vertical (ou vice-versa) para alcançar a recompensa. Evite movimentos diagonais, pois não são permitidos.

        **Formato da Saída:**
        Retorne APENAS o corpo da função JavaScript, sem a declaração `function(...) {{ ... }}`.

        **Exemplo de Corpo da Função de Saída:**
        ```javascript
        if (ry < py) {{
            return "up";
        }} else if (ry > py) {{
            return "down";
        }}
        if (rx < px) {{
            return "left";
        }} else if (rx > px) {{
            return "right";
        }}
        return null; // Retorna nulo se já estiver na posição
        ```

        Agora, crie o corpo da função JavaScript com base na sua análise.
        """

        # 3. Gerar a estratégia com o Gemini
        print("💡 Gerando estratégia com a API Gemini...")
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        
        # Limpa a resposta para extrair apenas o código
        js_code = response.text.strip()
        if js_code.startswith("```javascript"):
            js_code = js_code.split('
', 1)[1]
        if js_code.endswith("```"):
            js_code = js_code.rsplit('
', 1)[0]
        
        print("✨ Estratégia gerada:
", js_code)

        # 4. Implantar a estratégia no servidor de jogo
        print("🚀 Implantando a estratégia no servidor de jogo em tempo real...")
        sio.emit('deploy_strategy', {'code': js_code})

    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar-se ao Oráculo MCP: {e}")
        print("   Por favor, certifique-se de que o 'mcp_server' está rodando em 'http://127.0.0.1:8000'.")
        sio.disconnect()
    except Exception as e:
        print(f"🔥 Ocorreu um erro inesperado: {e}")
        sio.disconnect()

if __name__ == '__main__':
    if not os.getenv("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY") == "SUA_CHAVE_DE_API_AQUI":
        print("🚨 A chave de API do Gemini não foi encontrada.")
        print("   - Renomeie '.env.example' para '.env'.")
        print("   - Insira sua chave de API do Google Gemini no arquivo '.env'.")
    else:
        try:
            print("▶️  Iniciando o Agente MASP...")
            sio.connect(REALTIME_GAME_URL)
            sio.wait() # Mantém o script rodando enquanto a conexão estiver ativa
        except socketio.exceptions.ConnectionError as e:
            print(f"❌ Erro ao conectar-se ao servidor de jogo: {e}")
            print(f"   Por favor, certifique-se de que o 'realtime_game' server está rodando em '{REALTIME_GAME_URL}'.")
        except Exception as e:
            print(f"🔥 Ocorreu um erro inesperado durante a inicialização: {e}")

''