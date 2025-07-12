"""
Servidor MCP (Modelo) que expõe as regras do jogo para o agente MASP.
Este é o "Oráculo" que o agente consulta para aprender como jogar.
"""

from flask import Flask, jsonify
from flask_cors import CORS
import random

# Configurações do servidor
SERVER_NAME = "Block Picker Game Rules API"
SERVER_DESCRIPTION = "API que expõe as regras e ferramentas do jogo Block Picker"

# Inicializa o servidor Flask
app = Flask(__name__)
CORS(app)

# Simulação do motor do jogo
class SimpleGameEngine:
    def __init__(self):
        self.directions = ['up', 'down', 'left', 'right']
        self.player_pos = [5, 5]
        self.block_pos = [3, 3]
        self.score = 0
    
    def set_move(self, direction):
        if direction in self.directions:
            return True
        return False
    
    def get_score(self):
        return self.score
    
    def get_map(self):
        return """
        ####################
        #OOOOOOOOOOOOOOOOOO#
        #OOOOOOOOOOOOOOOOOO#
        #OOOOOOOOOOOOOOOOOO#
        #OOOOOOOOOOOOOOOOOO#
        #OOOOOOOOOOOOOOOOOO#
        #OOOOOOOOOOOOOOOOOO#
        #OOOOOOOOOOOOOOOOOO#
        #OOOOOOOOOOOOOOOOOO#
        #OOOOOOOOOOOOOOOOOO#
        ####################
        """
    
    def get_player_position(self):
        return self.player_pos
    
    def get_block_position(self):
        return self.block_pos
    
    def get_valid_directions(self):
        return self.directions

# Inicializa o motor do jogo
game_engine = SimpleGameEngine()

# Rotas da API
@app.route('/tools', methods=['GET'])
def get_tools():
    """Retorna todas as ferramentas disponíveis"""
    tools = [
        {
            "name": "mover",
            "description": "Move o jogador na direção especificada",
            "args": ["direcao"]
        },
        {
            "name": "pontuacao",
            "description": "Retorna a pontuação atual do jogador",
            "args": []
        },
        {
            "name": "mapa",
            "description": "Retorna o desenho do mapa atual",
            "args": []
        },
        {
            "name": "posicao_jogador",
            "description": "Retorna a posição atual do jogador",
            "args": []
        },
        {
            "name": "posicao_recompensa",
            "description": "Retorna a posição atual da recompensa",
            "args": []
        },
        {
            "name": "direcoes_validas",
            "description": "Retorna as direções válidas para movimento",
            "args": []
        },
        {
            "name": "regras_jogo",
            "description": "Retorna as regras básicas do jogo",
            "args": []
        }
    ]
    return jsonify(tools)

@app.route('/mover/<direcao>', methods=['GET'])
def mover(direcao):
    """Move o jogador na direção especificada"""
    if direcao in game_engine.directions:
        game_engine.set_move(direcao)
        return jsonify({"message": f"🎮 Movendo para {direcao}"})
    else:
        valid_dirs = ", ".join(game_engine.get_valid_directions())
        return jsonify({"error": f"❌ Direção inválida. Use: {valid_dirs}"}), 400

@app.route('/pontuacao', methods=['GET'])
def pontuacao():
    """Retorna a pontuação atual do jogador"""
    return jsonify({"pontuacao": f"🏆 Pontuação: {game_engine.get_score()}"})

@app.route('/mapa', methods=['GET'])
def mapa():
    """Retorna o desenho do mapa atual"""
    return jsonify({"mapa": f"🗺️ Mapa atual:\n{game_engine.get_map()}"})

@app.route('/posicao_jogador', methods=['GET'])
def posicao_jogador():
    """Retorna a posição atual do jogador"""
    pos = game_engine.get_player_position()
    return jsonify({"posicao": f"👤 Posição do jogador: ({pos[0]}, {pos[1]})"})

@app.route('/posicao_recompensa', methods=['GET'])
def posicao_recompensa():
    """Retorna a posição atual da recompensa"""
    pos = game_engine.get_block_position()
    return jsonify({"posicao": f"🎯 Posição da recompensa: ({pos[0]}, {pos[1]})"})

@app.route('/direcoes_validas', methods=['GET'])
def direcoes_validas():
    """Retorna as direções válidas para movimento"""
    directions = game_engine.get_valid_directions()
    return jsonify({"direcoes": f"🔄 Direções válidas: {', '.join(directions)}"})

@app.route('/regras_jogo', methods=['GET'])
def regras_jogo():
    """Retorna as regras básicas do jogo"""
    regras = """
    📖 REGRAS DO JOGO BLOCK PICKER:
    
    1. 🎯 OBJETIVO: Coletar o máximo de blocos vermelhos (R) possível
    2. 🎮 MOVIMENTO: Use as direções up, down, left, right
    3. 🚫 LIMITES: Não pode sair do tabuleiro (cercado por paredes #)
    4. 🏆 PONTUAÇÃO: Cada bloco coletado adiciona 1 ponto
    5. 👤 POSIÇÃO: O jogador é representado por 'P' no mapa
    6. 🎯 RECOMPENSA: Os blocos vermelhos são representados por 'R'
    7. ⬜ ESPAÇOS LIVRES: Representados por 'O'
    8. 🧱 PAREDES: Representadas por '#'
    
    O mapa usa coordenadas onde (0,0) é o canto superior esquerdo.
    """
    return jsonify({"regras": regras})

@app.route('/health', methods=['GET'])
def health():
    """Endpoint de saúde"""
    return jsonify({"status": "healthy", "service": SERVER_NAME})

def main():
    """Função principal do servidor MCP"""
    print("🚀 Servidor MCP (Oráculo de Regras) iniciando...")
    print(f"📡 Nome: {SERVER_NAME}")
    print(f"📝 Descrição: {SERVER_DESCRIPTION}")
    print("🔧 Ferramentas disponíveis:")
    print("   🎮 mover(direcao): Move o jogador")
    print("   🏆 pontuacao(): Retorna a pontuação")
    print("   🗺️ mapa(): Mostra o mapa atual")
    print("   👤 posicao_jogador(): Posição do jogador")
    print("   🎯 posicao_recompensa(): Posição da recompensa")
    print("   🔄 direcoes_validas(): Lista de direções válidas")
    print("   📖 regras_jogo(): Regras do jogo")
    print("🛑 Pressione Ctrl+C para parar.")
    
    try:
        app.run(host='127.0.0.1', port=8000, debug=False)
    except KeyboardInterrupt:
        print("\n🛑 Servidor MCP interrompido pelo usuário")
    except Exception as e:
        print(f"🔥 Erro no servidor MCP: {e}")

if __name__ == "__main__":
    main()