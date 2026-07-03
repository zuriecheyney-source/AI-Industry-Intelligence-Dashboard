"""验证 DeepSeek 配置"""
import asyncio
import sys
from app.core.config import settings
from app.core.ai_client import AIClientFactory

# 设置 UTF-8 输出（Windows 兼容）
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

async def test():
    print(f"当前 Provider: {settings.ai_provider}")
    print(f"DeepSeek API Key: {settings.deepseek_api_key[:20]}...")
    print(f"DeepSeek Model: {settings.deepseek_model}\n")
    
    client = AIClientFactory.get_client()
    print(f"客户端类型: {type(client).__name__}\n")
    
    try:
        result = await client.generate("用一句话介绍人工智能")
        print(f"[OK] DeepSeek 测试成功")
        print(f"回复: {result[:150]}...")
    except Exception as e:
        print(f"[ERROR] DeepSeek 测试失败: {e}")

if __name__ == "__main__":
    asyncio.run(test())