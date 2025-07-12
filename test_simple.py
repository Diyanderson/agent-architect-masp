#!/usr/bin/env python3
"""
Teste simples de conectividade para verificar se os componentes estão funcionando.
"""

import requests
import time
import socketio
import sys

def test_mcp_server():
    """Testa se o servidor MCP está respondendo"""
    print("🔮 Testando servidor MCP...")
    try:
        response = requests.get("http://127.0.0.1:8000/tools", timeout=5)
        if response.status_code == 200:
            tools = response.json()
            print(f"✅ Servidor MCP OK - {len(tools)} ferramentas disponíveis")
            return True
        else:
            print(f"❌ Servidor MCP retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar ao servidor MCP: {e}")
        return False

def test_game_server():
    """Testa se o servidor de jogo está respondendo"""
    print("🎮 Testando servidor de jogo...")
    try:
        response = requests.get("http://localhost:3000/api/status", timeout=5)
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Servidor de jogo OK - Status: {status['status']}")
            return True
        else:
            print(f"❌ Servidor de jogo retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar ao servidor de jogo: {e}")
        return False

def test_socket_connection():
    """Testa conexão Socket.IO"""
    print("🔌 Testando conexão Socket.IO...")
    try:
        sio = socketio.Client()
        connected = False
        
        @sio.event
        def connect():
            nonlocal connected
            connected = True
        
        sio.connect("http://localhost:3000")
        time.sleep(2)
        sio.disconnect()
        
        if connected:
            print("✅ Conexão Socket.IO OK")
            return True
        else:
            print("❌ Falha na conexão Socket.IO")
            return False
    except Exception as e:
        print(f"❌ Erro na conexão Socket.IO: {e}")
        return False

def main():
    """Função principal"""
    print("🧪 Teste de Conectividade - Agent Architect (MASP)")
    print("=" * 50)
    
    # Testa servidor MCP
    mcp_ok = test_mcp_server()
    
    # Testa servidor de jogo
    game_ok = test_game_server()
    
    # Testa Socket.IO
    socket_ok = test_socket_connection()
    
    # Resumo
    print("\n📊 Resumo dos Testes:")
    print(f"🔮 Servidor MCP: {'✅ OK' if mcp_ok else '❌ FALHOU'}")
    print(f"🎮 Servidor de Jogo: {'✅ OK' if game_ok else '❌ FALHOU'}")
    print(f"🔌 Socket.IO: {'✅ OK' if socket_ok else '❌ FALHOU'}")
    
    if mcp_ok and game_ok and socket_ok:
        print("\n🎉 Todos os testes passaram! O sistema está funcionando.")
        return 0
    else:
        print("\n⚠️ Alguns testes falharam. Verifique se os servidores estão rodando.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 