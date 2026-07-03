"""快速验证核心组件"""
import sys

print("=" * 50)
print("快速测试")
print("=" * 50)

# 1. 配置加载
try:
    from app.core.config import settings
    print("\n[OK] 配置加载")
    print(f"  AI: {settings.ai_provider}")
    print(f"  时区: {settings.timezone}")
except Exception as e:
    print(f"\n[ERROR] 配置失败: {e}")
    sys.exit(1)

# 2. 服务单例
try:
    from app.services.search_service import get_search_service
    from app.services.ai_service import get_ai_service
    from app.services.excel_service import get_excel_service
    from app.services.notification_service import get_notification_service
    
    get_search_service()
    get_ai_service()
    get_excel_service()
    get_notification_service()
    
    print("\n[OK] 服务单例")
except Exception as e:
    print(f"\n[ERROR] 服务单例失败: {e}")
    sys.exit(1)

# 3. 数据目录
try:
    from pathlib import Path
    data_dir = Path(settings.excel_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n[OK] 数据目录: {data_dir}")
except Exception as e:
    print(f"\n[ERROR] 数据目录失败: {e}")
    sys.exit(1)

# 4. 配置文件
try:
    import json
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
            industries = config.get("industries", [])
            print(f"\n[OK] 配置文件: {len(industries)} 个行业")
    else:
        print(f"\n[WARN] 配置文件不存在")
except Exception as e:
    print(f"\n[ERROR] 配置文件失败: {e}")

print("\n" + "=" * 50)
print("测试完成")
print("=" * 50)