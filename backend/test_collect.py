"""直接测试采集任务"""
import asyncio
import sys

async def main():
    print("开始测试采集...")
    
    try:
        from app.scheduler.tasks import trigger_manual_collection
        print("[OK] 导入成功")
        
        print("\n执行采集任务...")
        result = await trigger_manual_collection()
        
        print(f"\n结果:")
        print(f"  状态: {result.get('status')}")
        if result.get('status') == 'completed':
            print(f"  情报数: {result.get('intelligence_count', 0)}")
            print(f"  耗时: {result.get('duration_seconds', 0):.1f}秒")
            if result.get('industries'):
                print(f"  行业: {', '.join(result['industries'])}")
        elif result.get('status') == 'failed':
            print(f"  错误: {result.get('error')}")
            
    except Exception as e:
        print(f"\n[错误] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())