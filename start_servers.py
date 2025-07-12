#!/usr/bin/env python3
"""
Script para iniciar todos os servidores do Agent Architect (MASP) na ordem correta.
"""

import subprocess
import time
import requests
import sys
import os
from threading import Thread

class ServerManager:
    """Gerencia a inicialização e monitoramento dos servidores"""
    
    def __init__(self):
        self.processes = {}
        self.running = True
    
    def start_mcp_server(self):
        """Inicia o servidor MCP"""
        print("🔮 Iniciando servidor MCP (Oracle)...")
        try:
            process = subprocess.Popen(
                [sys.executable, "mcp_server/mcp_game_instance.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['mcp'] = process
            print("✅ Servidor MCP iniciado")
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor MCP: {e}")
            return False
    
    def start_game_server(self):
        """Inicia o servidor de jogo"""
        print("🎮 Iniciando servidor de jogo (Board)...")
        try:
            # Verifica se as dependências estão instaladas
            if not os.path.exists('realtime_game/node_modules'):
                print("📦 Instalando dependências do Node.js...")
                subprocess.run(['npm', 'install'], cwd='realtime_game', check=True)
            
            process = subprocess.Popen(
                ['node', 'server.js'],
                cwd='realtime_game',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['game'] = process
            print("✅ Servidor de jogo iniciado")
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar servidor de jogo: {e}")
            return False
    
    def wait_for_service(self, url, name, timeout=30):
        """Aguarda um serviço ficar disponível"""
        print(f"⏳ Aguardando {name} ficar disponível...")
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    print(f"✅ {name} está respondendo")
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        print(f"❌ {name} não respondeu no tempo limite")
        return False
    
    def start_agent(self):
        """Inicia o agente MASP"""
        print("🧠 Iniciando agente MASP (Brain)...")
        try:
            # Verifica se o arquivo .env existe
            if not os.path.exists('masp_agent/.env'):
                print("⚠️ Arquivo .env não encontrado, criando exemplo...")
                if os.path.exists('masp_agent/env.example'):
                    import shutil
                    shutil.copy('masp_agent/env.example', 'masp_agent/.env')
                    print("💡 Configure sua chave de API do Gemini no arquivo masp_agent/.env")
            
            process = subprocess.Popen(
                [sys.executable, "masp_agent/agent_masp.py"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['agent'] = process
            print("✅ Agente MASP iniciado")
            return True
        except Exception as e:
            print(f"❌ Erro ao iniciar agente MASP: {e}")
            return False
    
    def monitor_processes(self):
        """Monitora os processos em background"""
        while self.running:
            for name, process in self.processes.items():
                if process.poll() is not None:
                    print(f"⚠️ Processo {name} terminou inesperadamente")
            time.sleep(5)
    
    def cleanup(self):
        """Limpa todos os processos"""
        print("\n🛑 Encerrando todos os processos...")
        self.running = False
        
        for name, process in self.processes.items():
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ Processo {name} encerrado")
            except subprocess.TimeoutExpired:
                process.kill()
                print(f"⚠️ Processo {name} forçado a encerrar")
            except Exception as e:
                print(f"❌ Erro ao encerrar {name}: {e}")
    
    def run(self):
        """Executa a sequência de inicialização"""
        print("🚀 Iniciando Agent Architect (MASP)...")
        print("=" * 50)
        
        try:
            # 1. Inicia servidor MCP
            if not self.start_mcp_server():
                return False
            
            # 2. Aguarda servidor MCP ficar disponível
            if not self.wait_for_service("http://127.0.0.1:8000/tools", "Servidor MCP"):
                return False
            
            # 3. Inicia servidor de jogo
            if not self.start_game_server():
                return False
            
            # 4. Aguarda servidor de jogo ficar disponível
            if not self.wait_for_service("http://localhost:3000/api/status", "Servidor de Jogo"):
                return False
            
            # 5. Inicia agente MASP
            if not self.start_agent():
                return False
            
            print("\n🎉 Todos os componentes iniciados com sucesso!")
            print("📱 Acesse o jogo em: http://localhost:3000")
            print("🔮 API MCP em: http://127.0.0.1:8000")
            print("🧠 Agente MASP rodando em background")
            print("\n💡 Pressione Ctrl+C para parar todos os serviços")
            
            # Inicia monitoramento em background
            monitor_thread = Thread(target=self.monitor_processes, daemon=True)
            monitor_thread.start()
            
            # Aguarda indefinidamente
            while True:
                time.sleep(1)
                
        except KeyboardInterrupt:
            print("\n🛑 Interrompido pelo usuário")
        except Exception as e:
            print(f"🔥 Erro inesperado: {e}")
        finally:
            self.cleanup()

def main():
    """Função principal"""
    manager = ServerManager()
    try:
        manager.run()
    except Exception as e:
        print(f"🔥 Erro fatal: {e}")
        manager.cleanup()
        return 1
    return 0

if __name__ == "__main__":
    sys.exit(main()) 