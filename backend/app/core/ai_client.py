from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from app.core.config import settings


class AIClientBase(ABC):
    """AI客户端基类"""
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """生成文本"""
        pass


class DeepSeekClient(AIClientBase):
    """DeepSeek客户端"""
    
    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(
            api_key=settings.deepseek_api_key,
            base_url=settings.deepseek_base_url
        )
        self.model = settings.deepseek_model
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content


class OllamaClient(AIClientBase):
    """Ollama本地客户端"""
    
    def __init__(self):
        from openai import AsyncOpenAI
        self.client = AsyncOpenAI(
            api_key="ollama",  # Ollama不需要API key
            base_url=f"{settings.ollama_base_url}/v1"
        )
        self.model = settings.ollama_model
    
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.7,
            max_tokens=2000
        )
        return response.choices[0].message.content


class AIClientFactory:
    """AI客户端工厂"""
    
    _clients: Dict[str, AIClientBase] = {}
    
    @classmethod
    def get_client(cls, provider: Optional[str] = None) -> AIClientBase:
        """获取AI客户端实例（单例模式）"""
        provider = provider or settings.ai_provider
        
        if provider not in cls._clients:
            if provider == "deepseek":
                cls._clients[provider] = DeepSeekClient()
            elif provider == "ollama":
                cls._clients[provider] = OllamaClient()
            else:
                raise ValueError(f"不支持的AI提供商: {provider}")
        
        return cls._clients[provider]


# 便捷函数
async def generate_text(prompt: str, system_prompt: Optional[str] = None, 
                       provider: Optional[str] = None) -> str:
    """生成文本的便捷函数"""
    client = AIClientFactory.get_client(provider)
    return await client.generate(prompt, system_prompt)