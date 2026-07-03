"""诊断系统配置和API连通性"""
import sys
from pathlib import Path

print("=== 系统诊断 ===\n")

# 1. 检查配置
print("1. 检查配置...")
try:
    from app.core.config import settings
    print(f"  [OK] 配置加载")
    print(f"    AI Provider: {settings.ai_provider}")
    print(f"    Serper API: {'已配置' if settings.serper_api_key else '未配置'}")
    print(f"    飞书 Webhook: {'已配置' if settings.feishu_webhook_url else '未配置'}")
except Exception as e:
    print(f"  [错误] {e}")
    sys.exit(1)

# 2. 检查数据目录
print("\n2. 检查数据目录...")
data_dir = Path(settings.excel_dir)
if data_dir.exists():
    files = list(data_dir.glob("*.xlsx"))
    print(f"  [OK] 目录存在: {data_dir}")
    print(f"    Excel文件数: {len(files)}")
    for f in files:
        print(f"      - {f.name}")
else:
    print(f"  [警告] 目录不存在: {data_dir}")

# 3. 测试 Serper API
print("\n3. 测试搜索API...")
if settings.serper_api_key:
    try:
        import httpx
        response = httpx.post(
            "https://google.serper.dev/search",
            headers={"X-API-KEY": settings.serper_api_key},
            json={"q": "test"},
            timeout=5.0
        )
        if response.status_code == 200:
            print(f"  [OK] Serper API 连通")
        else:
            print(f"  [错误] 状态码: {response.status_code}")
    except Exception as e:
        print(f"  [错误] {e}")
else:
    print("  [跳过] 未配置API密钥")

# 4. 测试 AI API
print("\n4. 测试AI API...")
try:
    if settings.ai_provider == "deepseek" and settings.deepseek_api_key:
        from openai import OpenAI
        client = OpenAI(api_key=settings.deepseek_api_key, base_url=settings.deepseek_base_url)
        response = client.chat.completions.create(
            model=settings.deepseek_model,
            messages=[{"role": "user", "content": "test"}],
            max_tokens=5
        )
        print(f"  [OK] DeepSeek API 连通")
    else:
        print(f"  [跳过] 当前provider: {settings.ai_provider} 或未配置API Key")
except Exception as e:
    print(f"  [错误] {e}")

print("\n=== 诊断完成 ===")