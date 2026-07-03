"""手动触发采集并等待完成"""
import asyncio
import sys
sys.path.insert(0, '.')

from app.scheduler.tasks import trigger_manual_collection

async def main():
    print("开始采集情报...")
    result = await trigger_manual_collection()
    print(f"\n采集完成:")
    print(f"  状态: {result.get('status')}")
    print(f"  情报数量: {result.get('intelligence_count', 0)}")
    print(f"  耗时: {result.get('duration_seconds', 0):.1f}秒")
    if result.get('industries'):
        print(f"  行业: {', '.join(result['industries'])}")

if __name__ == "__main__":
    asyncio.run(main())