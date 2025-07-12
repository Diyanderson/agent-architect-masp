import os
from typing import Optional

# Tenta carregar dotenv se disponível
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Se dotenv não estiver disponível, usa apenas os.environ
    pass

class Config:
    """Configurações centralizadas do agente MASP"""
    
    # API Keys
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    
    # URLs dos serviços
    MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://127.0.0.1:8000")
    REALTIME_GAME_URL = os.getenv("REALTIME_GAME_URL", "http://localhost:3000")
    
    # Configurações do agente
    AGENT_ID = "ai_agent_masp"
    
    # Configurações do modelo
    MODEL_NAME = "gemini-pro"
    
    # Timeouts
    REQUEST_TIMEOUT = 30
    CONNECTION_TIMEOUT = 10
    
    @classmethod
    def validate(cls) -> bool:
        """Valida se todas as configurações necessárias estão presentes"""
        if not cls.GEMINI_API_KEY or cls.GEMINI_API_KEY == "SUA_CHAVE_DE_API_AQUI":
            raise ValueError(
                "Chave de API do Gemini não configurada. "
                "Configure GEMINI_API_KEY no arquivo .env ou como variável de ambiente"
            )
        return True
    
    @classmethod
    def get_status(cls) -> dict:
        """Retorna o status das configurações"""
        return {
            "gemini_api_key_configured": bool(cls.GEMINI_API_KEY and cls.GEMINI_API_KEY != "SUA_CHAVE_DE_API_AQUI"),
            "mcp_server_url": cls.MCP_SERVER_URL,
            "realtime_game_url": cls.REALTIME_GAME_URL,
            "model_name": cls.MODEL_NAME,
            "agent_id": cls.AGENT_ID
        } 