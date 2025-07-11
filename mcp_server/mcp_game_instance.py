# Este servidor expõe as ferramentas do jogo para o agente MASP aprender as regras.
# Ele roda na porta 8000 por padrão (via FastMCP).
import pygame
import random
from mcp.server.fastmcp import FastMCP

# Game settings
WIDTH, HEIGHT = 400, 400
BLOCK_SIZE = 40
FPS = 10

# Directions
DIRECTIONS = {
    'up': (0, -1),
    'down': (0, 1),
    'left': (-1, 0),
    'right': (1, 0)
}

# MCP server
mcp = FastMCP("Block Picker Game Rules API")

class Game:
    def __init__(self):
        rows = HEIGHT // BLOCK_SIZE
        cols = WIDTH // BLOCK_SIZE
        px, py = cols // 2, rows // 2
        if px == 0: px = 1
        if py == 0: py = 1
        self.player_pos = [px * BLOCK_SIZE, py * BLOCK_SIZE]
        self.block_pos = self.random_block()
        self.score = 0
        self.move_command = None

    def random_block(self):
        rows = HEIGHT // BLOCK_SIZE
        cols = WIDTH // BLOCK_SIZE
        while True:
            x = random.randint(1, cols - 2) * BLOCK_SIZE
            y = random.randint(1, rows - 2) * BLOCK_SIZE
            if [x, y] != self.player_pos:
                return [x, y]

    def move_player(self, direction):
        if direction in DIRECTIONS:
            dx, dy = DIRECTIONS[direction]
            new_x = self.player_pos[0] + dx * BLOCK_SIZE
            new_y = self.player_pos[1] + dy * BLOCK_SIZE
            rows = HEIGHT // BLOCK_SIZE
            cols = WIDTH // BLOCK_SIZE
            col = new_x // BLOCK_SIZE
            row = new_y // BLOCK_SIZE
            if 1 <= col < cols-1 and 1 <= row < rows-1:
                self.player_pos = [new_x, new_y]

    def update(self):
        if self.player_pos == self.block_pos:
            self.score += 1
            self.block_pos = self.random_block()

    def set_move(self, direction):
        self.move_command = direction

    def get_score(self):
        return self.score

    def get_map(self):
        """Retorna uma string representando o mapa do jogo com cerca (#), O para livre, P para player e R para recompensa."""
        rows = HEIGHT // BLOCK_SIZE
        cols = WIDTH // BLOCK_SIZE
        grid = [['O' for _ in range(cols)] for _ in range(rows)]
        for y in range(rows):
            grid[y][0] = '#'; grid[y][cols-1] = '#'
        for x in range(cols):
            grid[0][x] = '#'; grid[rows-1][x] = '#'
        px, py = self.player_pos[0] // BLOCK_SIZE, self.player_pos[1] // BLOCK_SIZE
        bx, by = self.block_pos[0] // BLOCK_SIZE, self.block_pos[1] // BLOCK_SIZE
        grid[py][px] = 'P'
        grid[by][bx] = 'R'
        return '\n'.join(''.join(row) for row in grid)

game = Game()

@mcp.tool()
def mover(direcao: str) -> str:
    """Move o jogador na direção especificada (up, down, left, right)."""
    if direcao in DIRECTIONS:
        game.set_move(direcao)
        return f"Movendo para {direcao}"
    else:
        return "Direção inválida. Use: up, down, left, right."

@mcp.tool()
def pontuacao() -> str:
    """Retorna a pontuação atual do jogador."""
    return f"Pontuação: {game.get_score()}"

@mcp.tool()
def mapa() -> str:
    """Retorna o desenho do mapa atual (P=player, R=recompensa, O=espaço livre, #=parede)."""
    return game.get_map()

if __name__ == "__main__":
    print("Servidor MCP (Oraculo de Regras) rodando em http://127.0.0.1:8000")
    print("Este servidor apenas expoe as ferramentas do jogo para o Agente MASP.")
    print("Pressione Ctrl+C para parar.")
    mcp.run() # Usar o padrão, que é HTTP