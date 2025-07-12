"""
Módulo para gerenciar o contexto das regras do jogo e comunicação com o oráculo MCP.
Responsável por aprender e interpretar as regras do jogo.
"""

import requests
from typing import List, Dict, Any, Optional
try:
    from config import Config
except ImportError:
    # Fallback se config não estiver disponível
    class Config:
        MCP_SERVER_URL = "http://127.0.0.1:8000"
        REQUEST_TIMEOUT = 30


class GameRulesContext:
    """Gerencia o contexto das regras do jogo obtidas do oráculo MCP"""
    
    def __init__(self, mcp_server_url: str | None = None):
        self.mcp_server_url = mcp_server_url if mcp_server_url is not None else Config.MCP_SERVER_URL
        self.game_tools = []
        self.tools_description = ""
    
    def learn_rules(self) -> bool:
        """
        Aprende as regras do jogo consultando o oráculo MCP.
        
        Returns:
            bool: True se conseguiu aprender as regras, False caso contrário
        """
        try:
            print("🧠 Consultando o oráculo MCP para aprender as regras do jogo...")
            response = requests.get(
                f"{self.mcp_server_url}/tools",
                timeout=Config.REQUEST_TIMEOUT
            )
            response.raise_for_status()
            
            self.game_tools = response.json()
            self._build_tools_description()
            
            print(f"📚 Regras aprendidas com sucesso! {len(self.game_tools)} ferramentas disponíveis.")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao conectar-se ao oráculo MCP: {e}")
            print(f"   Certifique-se de que o servidor MCP está rodando em {self.mcp_server_url}")
            return False
        except Exception as e:
            print(f"🔥 Erro inesperado ao aprender regras: {e}")
            return False
    
    def _build_tools_description(self):
        """Constrói a descrição das ferramentas disponíveis"""
        descriptions = []
        for tool in self.game_tools:
            args_str = ', '.join(tool.get('args', []))
            desc = f"- `{tool['name']}({args_str})`: {tool['description']}"
            descriptions.append(desc)
        
        self.tools_description = "\n".join(descriptions)
    
    def get_strategy_prompt(self) -> str:
        """
        Gera o prompt para criação de estratégia baseado nas regras aprendidas.
        
        Returns:
            str: Prompt formatado para o modelo de IA
        """
        return f"""
        Você é um agente de IA especialista em programação e jogos. Sua tarefa é criar uma estratégia para um jogo simples.

        **Objetivo do Jogo:**
        O jogador ('P') deve coletar a recompensa ('R') em um mapa cercado por paredes ('#').

        **Regras e Ferramentas Disponíveis (via API):**
        {self.tools_description}
        O mapa tem coordenadas onde (0,0) é o canto superior esquerdo.

        **Sua Tarefa:**
        Crie uma função JavaScript que receba a posição do jogador `playerPos` (um objeto com `x` e `y`) e a posição da recompensa `rewardPos` (também com `x` e `y`) e retorne a próxima melhor direção para o jogador se mover.
        As direções de retorno possíveis são: "up", "down", "left", "right".

        **Requisitos da Estratégia:**
        - A lógica deve ser contida em uma única função.
        - A função deve ser eficiente e direta.
        - A estratégia deve ser inteligente: mova-se na direção horizontal e depois na vertical (ou vice-versa) para alcançar a recompensa.
        - Evite movimentos diagonais, pois não são permitidos.
        - Considere a distância Manhattan para otimizar o caminho.

        **Formato da Saída:**
        Retorne APENAS o corpo da função JavaScript, sem a declaração `function(...) {{ ... }}`.

        **Exemplo de Corpo da Função de Saída:**
        ```javascript
        // Estratégia otimizada: primeiro alinha horizontalmente, depois verticalmente
        if (rx < px) {{
            return "left";
        }} else if (rx > px) {{
            return "right";
        }}
        if (ry < py) {{
            return "up";
        }} else if (ry > py) {{
            return "down";
        }}
        return null; // Retorna nulo se já estiver na posição
        ```

        Agora, crie o corpo da função JavaScript com base na sua análise das regras do jogo.
        """
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Retorna a lista de ferramentas disponíveis"""
        return self.game_tools
    
    def get_tools_description(self) -> str:
        """Retorna a descrição formatada das ferramentas"""
        return self.tools_description