"""基础配置和服务测试"""
import sys
from pathlib import Path

# 测试配置加载
print("=" * 60)
print("AI行业情报系统 - 基础测试")
print("=" * 60)

print("\n1. 测试配置加载...")
try:
    from app.core.config import settings
    print(f"[OK] 配置加载成功")
    print(f"  - AI Provider: {settings.ai_provider}")
    print(f"  - 数据目录: {settings.excel_dir}")
    print(f"  - 定时时间: {settings.schedule_times_list}")
    print(f"  - 时区: {settings.timezone}")
except Exception as e:
    print(f"[ERROR] 配置加载失败: {e}")
    sys.exit(1)

print("\n2. 测试服务单例获取...")
try:
    from app.services.search_service import get_search_service
    from app.services.ai_service import get_ai_service
    from app.services.excel_service import get_excel_service
    from app.services.notification_service import get_notification_service
    
    search_service = get_search_service()
    ai_service = get_ai_service()
    excel_service = get_excel_service()
    notification_service = get_notification_service()
    
    print(f"[OK] 所有服务单例获取成功")
except Exception as e:
    print(f"[ERROR] 服务获取失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3. 测试数据目录...")
try:
    data_dir = Path(settings.excel_dir)
    if not data_dir.exists():
        data_dir.mkdir(parents=True, exist_ok=True)
        print(f"[OK] 创建数据目录: {data_dir}")
    else:
        print(f"[OK] 数据目录已存在: {data_dir}")
except Exception as e:
    print(f"[ERROR] 数据目录检查失败: {e}")
    sys.exit(1)

print("\n4. 测试行业配置加载...")
try:
    import json
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
            industries = config.get("industries", [])
            print(f"[OK] 配置文件加载成功，共 {len(industries)} 个行业")
            for ind in industries:
                status = "启用" if ind.get("enabled") else "禁用"
                print(f"  - {ind['name']}: {len(ind['keywords'])} 个关键词 [{status}]")
    else:
        print(f"[WARN] 配置文件不存在: {config_path}")
except Exception as e:
    print(f"[ERROR] 配置文件加载失败: {e}")

print("\n5. 检查API密钥配置...")
api_keys = {
    "Serper (搜索)": settings.serper_api_key,
    "飞书Webhook": settings.feishu_webhook_url,
    f"{settings.ai_provider.upper()} API": getattr(settings, f"{settings.ai_provider}_api_key", None)
}

for name, key in api_keys.items():
    if key:
        masked = f"{key[:10]}...{key[-4:]}" if len(key) > 14 else "***"
        print(f"[OK] {name}: {masked}")
    else:
        print(f"[WARN] {name}: 未配置")

print("\n" + "=" * 60)
print("基础测试完成")
print("=" * 60)