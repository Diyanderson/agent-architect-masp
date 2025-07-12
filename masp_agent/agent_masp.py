"""
Agente MASP (Modelo-Agente-Sistema-Plataforma)
O cérebro do sistema que aprende regras e gera estratégias de jogo.
"""

import socketio
import time
from typing import Optional

try:
    from config import Config
except ImportError:
    class Config:
        GEMINI_API_KEY = ""
        MCP_SERVER_URL = "http://127.0.0.1:8000"
        REALTIME_GAME_URL = "http://localhost:3000"
        AGENT_ID = "ai_agent_masp"
        MODEL_NAME = "gemini-pro"
        REQUEST_TIMEOUT = 30
        CONNECTION_TIMEOUT = 10
        
        @classmethod
        def validate(cls):
            if not cls.GEMINI_API_KEY or cls.GEMINI_API_KEY == "SUA_CHAVE_DE_API_AQUI":
                raise ValueError("Chave de API do Gemini não configurada")
            return True

try:
    from game_rules_context import GameRulesContext
except ImportError:
    class GameRulesContext:
        def __init__(self, mcp_server_url=None):
            self.mcp_server_url = mcp_server_url or "http://127.0.0.1:8000"
            self.game_tools = []
            self.tools_description = ""
        
        def learn_rules(self):
            print("⚠️ GameRulesContext não disponível - usando modo simulado")
            return True
        
        def get_strategy_prompt(self):
            return "Prompt simulado para estratégia"

try:
    from strategy_generator import StrategyGenerator
except ImportError:
    class StrategyGenerator:
        def __init__(self):
            print("⚠️ StrategyGenerator não disponível - usando estratégia padrão")
        
        def generate_strategy(self, prompt):
            print("⚠️ Gerando estratégia padrão")
            return """
            if (rx < px) {
                return "left";
            } else if (rx > px) {
                return "right";
            }
            if (ry < py) {
                return "up";
            } else if (ry > py) {
                return "down";
            }
            return null;
            """
        
        def validate_strategy(self, js_code):
            return True


class MaspAgent:
    """Agente MASP principal que coordena aprendizado e implantação de estratégias"""
    
    def __init__(self):
        self.sio = socketio.Client()
        self.rules_context = GameRulesContext()
        self.strategy_generator = StrategyGenerator()
        self._setup_socket_handlers()
    
    def _setup_socket_handlers(self):
        """Configura os handlers de eventos do Socket.IO"""
        
        @self.sio.event
        def connect():
            print("🔗 Agente conectado ao servidor de jogo.")
            self._learn_and_deploy_strategy()
        
        @self.sio.event
        def disconnect():
            print("🔌 Agente desconectado do servidor de jogo.")
        
        @self.sio.event
        def strategy_deployed(data):
            if data['status'] == 'success':
                print("✅ Estratégia implantada com sucesso no servidor de jogo!")
            else:
                print(f"❌ Falha ao implantar estratégia: {data.get('error', 'Erro desconhecido')}")
            # Desconecta após a tentativa de implantação
            self.sio.disconnect()
    
    def _learn_and_deploy_strategy(self):
        """
        Processo principal do agente:
        1. Aprende as regras do jogo
        2. Gera uma estratégia
        3. Implanta a estratégia no servidor
        """
        try:
            # 1. Aprender regras do jogo
            if not self.rules_context.learn_rules():
                print("❌ Falha ao aprender regras do jogo. Abortando...")
                self.sio.disconnect()
                return
            
            # 2. Gerar estratégia
            prompt = self.rules_context.get_strategy_prompt()
            js_code = self.strategy_generator.generate_strategy(prompt)
            
            if not js_code:
                print("❌ Falha ao gerar estratégia. Abortando...")
                self.sio.disconnect()
                return
            
            # 3. Validar estratégia
            if not self.strategy_generator.validate_strategy(js_code):
                print("❌ Estratégia gerada é inválida. Abortando...")
                self.sio.disconnect()
                return
            
            # 4. Implantar estratégia
            print("🚀 Implantando estratégia no servidor de jogo...")
            self.sio.emit('deploy_strategy', {'code': js_code})
            
        except Exception as e:
            print(f"🔥 Erro inesperado no processo de aprendizado: {e}")
            self.sio.disconnect()
    
    def start(self):
        """Inicia o agente MASP"""
        try:
            print("▶️ Iniciando o Agente MASP...")
            self.sio.connect(Config.REALTIME_GAME_URL)
            self.sio.wait()  # Mantém o script rodando
            
        except socketio.exceptions.ConnectionError as e:
            print(f"❌ Erro ao conectar-se ao servidor de jogo: {e}")
            print(f"   Certifique-se de que o servidor está rodando em {Config.REALTIME_GAME_URL}")
        except Exception as e:
            print(f"🔥 Erro inesperado durante a inicialização: {e}")
    
    def stop(self):
        """Para o agente MASP"""
        if self.sio.connected:
            self.sio.disconnect()


def main():
    """Função principal para executar o agente"""
    try:
        # Validar configurações
        Config.validate()
        
        # Criar e iniciar o agente
        agent = MaspAgent()
        agent.start()
        
    except ValueError as e:
        print(f"🚨 Erro de configuração: {e}")
        print("   Configure o arquivo .env com sua chave de API do Gemini")
    except KeyboardInterrupt:
        print("\n🛑 Agente interrompido pelo usuário")
    except Exception as e:
        print(f"🔥 Erro inesperado: {e}")


if __name__ == '__main__':
    main()
