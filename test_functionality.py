#!/usr/bin/env python3
"""
Script de teste para verificar a funcionalidade de todos os componentes do projeto MASP.
"""

import subprocess
import time
import requests
import socketio
import sys
import os
from typing import Dict, Any

# Configurações de teste
TEST_TIMEOUT = 30
SERVICES = {
    'mcp_server': {
        'port': 8000,
        'url': 'http://127.0.0.1:8000',
        'name': 'MCP Server (Oracle)',
        'emoji': '🔮'
    },
    'realtime_game': {
        'port': 3000,
        'url': 'http://localhost:3000',
        'name': 'Real-time Game Server (Board)',
        'emoji': '🎮'
    }
}

class TestRunner:
    """Executa testes de funcionalidade para todos os componentes"""
    
    def __init__(self):
        self.results = {}
        self.processes = {}
    
    def print_header(self, message: str):
        """Imprime um cabeçalho formatado"""
        print(f"\n{'='*60}")
        print(f"🧪 {message}")
        print(f"{'='*60}")
    
    def print_section(self, message: str):
        """Imprime uma seção formatada"""
        print(f"\n📋 {message}")
        print("-" * 40)
    
    def print_result(self, service: str, success: bool, message: str = ""):
        """Imprime o resultado de um teste"""
        emoji = "✅" if success else "❌"
        status = "PASSOU" if success else "FALHOU"
        print(f"{emoji} {service}: {status}")
        if message:
            print(f"   💬 {message}")
    
    def check_port_available(self, port: int) -> bool:
        """Verifica se uma porta está disponível"""
        import socket
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return True
        except OSError:
            return False
    
    def wait_for_service(self, url: str, timeout: int = 10) -> bool:
        """Aguarda um serviço ficar disponível"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(0.5)
        return False
    
    def test_mcp_server(self) -> Dict[str, Any]:
        """Testa o servidor MCP"""
        self.print_section("Testando Servidor MCP (Oracle)")
        
        # Verifica se a porta está disponível
        if not self.check_port_available(SERVICES['mcp_server']['port']):
            return {
                'success': False,
                'message': f"Porta {SERVICES['mcp_server']['port']} já está em uso"
            }
        
        try:
            # Inicia o servidor MCP
            print("🚀 Iniciando servidor MCP...")
            process = subprocess.Popen(
                [sys.executable, 'mcp_server/mcp_game_instance.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['mcp_server'] = process
            
            # Aguarda o servidor inicializar
            if self.wait_for_service(SERVICES['mcp_server']['url']):
                print("✅ Servidor MCP iniciado com sucesso")
                
                # Testa a API de ferramentas
                try:
                    response = requests.get(f"{SERVICES['mcp_server']['url']}/tools")
                    if response.status_code == 200:
                        tools = response.json()
                        print(f"📚 {len(tools)} ferramentas disponíveis")
                        return {'success': True, 'message': f"{len(tools)} ferramentas carregadas"}
                    else:
                        return {'success': False, 'message': f"API retornou status {response.status_code}"}
                except Exception as e:
                    return {'success': False, 'message': f"Erro ao testar API: {e}"}
            else:
                return {'success': False, 'message': "Servidor não respondeu no tempo limite"}
                
        except Exception as e:
            return {'success': False, 'message': f"Erro ao iniciar servidor: {e}"}
    
    def test_realtime_game_server(self) -> Dict[str, Any]:
        """Testa o servidor de jogo em tempo real"""
        self.print_section("Testando Servidor de Jogo em Tempo Real (Board)")
        
        # Verifica se a porta está disponível
        if not self.check_port_available(SERVICES['realtime_game']['port']):
            return {
                'success': False,
                'message': f"Porta {SERVICES['realtime_game']['port']} já está em uso"
            }
        
        try:
            # Verifica se o Node.js está disponível
            try:
                subprocess.run(['node', '--version'], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                return {'success': False, 'message': "Node.js não encontrado no PATH"}
            
            # Verifica se as dependências estão instaladas
            if not os.path.exists('realtime_game/node_modules'):
                print("📦 Instalando dependências do Node.js...")
                subprocess.run(['npm', 'install'], cwd='realtime_game', check=True)
            
            # Inicia o servidor de jogo
            print("🚀 Iniciando servidor de jogo...")
            process = subprocess.Popen(
                ['node', 'server.js'],
                cwd='realtime_game',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            self.processes['realtime_game'] = process
            
            # Aguarda o servidor inicializar
            if self.wait_for_service(SERVICES['realtime_game']['url']):
                print("✅ Servidor de jogo iniciado com sucesso")
                
                # Testa a API de status
                try:
                    response = requests.get(f"{SERVICES['realtime_game']['url']}/api/status")
                    if response.status_code == 200:
                        status = response.json()
                        print(f"📊 Status: {status['status']}")
                        return {'success': True, 'message': "Servidor respondendo corretamente"}
                    else:
                        return {'success': False, 'message': f"API retornou status {response.status_code}"}
                except Exception as e:
                    return {'success': False, 'message': f"Erro ao testar API: {e}"}
            else:
                return {'success': False, 'message': "Servidor não respondeu no tempo limite"}
                
        except Exception as e:
            return {'success': False, 'message': f"Erro ao iniciar servidor: {e}"}
    
    def test_agent_connection(self) -> Dict[str, Any]:
        """Testa a conexão do agente MASP"""
        self.print_section("Testando Conexão do Agente MASP (Brain)")
        
        try:
            # Verifica se o servidor de jogo está rodando
            if not self.wait_for_service(SERVICES['realtime_game']['url'], timeout=5):
                return {'success': False, 'message': "Servidor de jogo não está disponível"}
            
            # Testa conexão Socket.IO
            sio = socketio.Client()
            connected = False
            
            @sio.event
            def connect():
                nonlocal connected
                connected = True
            
            sio.connect(SERVICES['realtime_game']['url'])
            time.sleep(2)
            sio.disconnect()
            
            if connected:
                return {'success': True, 'message': "Conexão Socket.IO estabelecida"}
            else:
                return {'success': False, 'message': "Falha na conexão Socket.IO"}
                
        except Exception as e:
            return {'success': False, 'message': f"Erro ao testar conexão: {e}"}
    
    def test_python_dependencies(self) -> Dict[str, Any]:
        """Testa as dependências Python"""
        self.print_section("Testando Dependências Python")
        
        required_modules = [
            'requests',
            'socketio',
            'google.generativeai'
        ]
        
        missing_modules = []
        for module in required_modules:
            try:
                __import__(module)
                print(f"✅ {module}")
            except ImportError:
                print(f"❌ {module}")
                missing_modules.append(module)
        
        if missing_modules:
            return {
                'success': False,
                'message': f"Módulos faltando: {', '.join(missing_modules)}"
            }
        else:
            return {'success': True, 'message': "Todas as dependências Python estão disponíveis"}
    
    def run_all_tests(self):
        """Executa todos os testes"""
        self.print_header("INICIANDO TESTES DE FUNCIONALIDADE MASP")
        
        try:
            # Testa dependências Python
            result = self.test_python_dependencies()
            self.print_result("Dependências Python", result['success'], result['message'])
            self.results['python_deps'] = result
            
            # Testa servidor MCP
            result = self.test_mcp_server()
            self.print_result("Servidor MCP", result['success'], result['message'])
            self.results['mcp_server'] = result
            
            # Testa servidor de jogo
            result = self.test_realtime_game_server()
            self.print_result("Servidor de Jogo", result['success'], result['message'])
            self.results['realtime_game'] = result
            
            # Testa conexão do agente
            result = self.test_agent_connection()
            self.print_result("Conexão do Agente", result['success'], result['message'])
            self.results['agent_connection'] = result
            
            # Resumo final
            self.print_summary()
            
        finally:
            self.cleanup()
    
    def print_summary(self):
        """Imprime o resumo dos testes"""
        self.print_header("RESUMO DOS TESTES")
        
        passed = sum(1 for result in self.results.values() if result['success'])
        total = len(self.results)
        
        print(f"📊 Resultado: {passed}/{total} testes passaram")
        
        if passed == total:
            print("🎉 Todos os testes passaram! O sistema está pronto para uso.")
        else:
            print("⚠️ Alguns testes falharam. Verifique os erros acima.")
        
        for test_name, result in self.results.items():
            status = "✅ PASSOU" if result['success'] else "❌ FALHOU"
            print(f"   {status}: {test_name}")
    
    def cleanup(self):
        """Limpa os processos iniciados"""
        print("\n🧹 Limpando processos...")
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


def main():
    """Função principal"""
    print("🚀 Iniciando testes de funcionalidade do projeto MASP...")
    
    runner = TestRunner()
    runner.run_all_tests()


if __name__ == "__main__":
    main() 