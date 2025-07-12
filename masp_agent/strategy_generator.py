"""
Módulo para gerar estratégias de jogo usando modelos de IA.
Responsável por criar e otimizar estratégias baseadas nas regras aprendidas.
"""

from typing import Optional
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    genai = None

try:
    from config import Config
except ImportError:
    # Fallback se config não estiver disponível
    class Config:
        GEMINI_API_KEY = ""
        MODEL_NAME = "gemini-pro"


class StrategyGenerator:
    """Gerencia a geração de estratégias usando modelos de IA"""
    
    def __init__(self):
        if GEMINI_AVAILABLE:
            genai.configure(api_key=Config.GEMINI_API_KEY)
            self.model = genai.GenerativeModel(Config.MODEL_NAME)
        else:
            self.model = None
            print("⚠️ Google Gemini não disponível - usando estratégia padrão")
    
    def generate_strategy(self, prompt: str) -> Optional[str]:
        """
        Gera uma estratégia de jogo usando o modelo de IA.
        
        Args:
            prompt: Prompt detalhado para geração da estratégia
            
        Returns:
            str: Código JavaScript da estratégia gerada, ou None se falhar
        """
        try:
            print("💡 Gerando estratégia com a API Gemini...")
            
            if not GEMINI_AVAILABLE or not self.model:
                print("⚠️ Usando estratégia padrão (Gemini não disponível)")
                return self._get_default_strategy()
            
            response = self.model.generate_content(prompt)
            
            # Limpa a resposta para extrair apenas o código
            js_code = self._extract_js_code(response.text)
            
            if js_code:
                print("✨ Estratégia gerada com sucesso!")
                print(f"📝 Código gerado:\n{js_code}")
                return js_code
            else:
                print("❌ Não foi possível extrair código JavaScript da resposta")
                return self._get_default_strategy()
                
        except Exception as e:
            print(f"🔥 Erro ao gerar estratégia: {e}")
            print("🔄 Usando estratégia padrão como fallback")
            return self._get_default_strategy()
    
    def _get_default_strategy(self) -> str:
        """Retorna uma estratégia padrão quando a IA não está disponível"""
        return """
        // Estratégia padrão: primeiro horizontal, depois vertical
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
    
    def _extract_js_code(self, response_text: str) -> Optional[str]:
        """
        Extrai o código JavaScript da resposta do modelo.
        
        Args:
            response_text: Texto completo da resposta
            
        Returns:
            str: Código JavaScript limpo, ou None se não conseguir extrair
        """
        text = response_text.strip()
        
        # Remove blocos de código markdown se presentes
        if text.startswith("```javascript"):
            text = text.split('\n', 1)[1]
        elif text.startswith("```js"):
            text = text.split('\n', 1)[1]
        elif text.startswith("```"):
            text = text.split('\n', 1)[1]
        
        if text.endswith("```"):
            text = text.rsplit('\n', 1)[0]
        
        # Remove linhas vazias no início e fim
        text = text.strip()
        
        # Validação básica: deve conter pelo menos uma direção
        directions = ['up', 'down', 'left', 'right']
        if not any(direction in text for direction in directions):
            print("⚠️ Código gerado não parece conter direções válidas")
            return None
        
        return text
    
    def validate_strategy(self, js_code: str) -> bool:
        """
        Valida se a estratégia gerada é válida.
        
        Args:
            js_code: Código JavaScript da estratégia
            
        Returns:
            bool: True se a estratégia é válida, False caso contrário
        """
        try:
            # Testa se o código pode ser compilado
            test_function = f"""
            function testStrategy(playerPos, rewardPos) {{
                const {{ x: px, y: py }} = playerPos;
                const {{ x: rx, y: ry }} = rewardPos;
                {js_code}
            }}
            """
            
            # Tenta criar a função (validação de sintaxe)
            exec(test_function)
            
            # Testa com valores de exemplo
            test_function = f"""
            function testStrategy(playerPos, rewardPos) {{
                const {{ x: px, y: py }} = playerPos;
                const {{ x: rx, y: ry }} = rewardPos;
                {js_code}
            }}
            testStrategy({{x: 1, y: 1}}, {{x: 2, y: 2}});
            """
            
            exec(test_function)
            print("✅ Estratégia validada com sucesso!")
            return True
            
        except Exception as e:
            print(f"❌ Estratégia inválida: {e}")
            return False 