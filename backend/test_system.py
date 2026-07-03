"""系统功能测试脚本"""
import asyncio
import json
from datetime import datetime
from pathlib import Path

from app.core.config import settings
from app.services.search_service import get_search_service
from app.services.ai_service import get_ai_service
from app.services.excel_service import get_excel_service
from app.services.notification_service import get_notification_service


async def test_search():
    """测试搜索服务"""
    print("\n=== 测试搜索服务 ===")
    search_service = get_search_service()
    
    try:
        results = await search_service.search("人工智能 最新", max_results=3)
        print(f"✓ 搜索成功，找到 {len(results)} 条结果")
        if results:
            print(f"  示例标题: {results[0]['title'][:50]}...")
        return True
    except Exception as e:
        print(f"✗ 搜索失败: {e}")
        return False


async def test_ai_summary():
    """测试AI总结服务"""
    print("\n=== 测试AI总结服务 ===")
    ai_service = get_ai_service()
    
    test_articles = [
        {
            "title": "DeepSeek发布新一代模型，性能大幅提升",
            "snippet": "DeepSeek今日宣布推出最新一代大语言模型，在多个基准测试中表现优异...",
            "link": "https://example.com/gpt5"
        }
    ]
    
    try:
        summary = await ai_service.summarize_articles("AI板块", test_articles)
        print(f"✓ AI总结成功")
        print(f"  标题: {summary['title'][:50]}...")
        print(f"  分类: {summary['category']}")
        print(f"  重要度: {summary['importance']}")
        return True
    except Exception as e:
        print(f"✗ AI总结失败: {e}")
        return False


def test_excel_service():
    """测试Excel服务"""
    print("\n=== 测试Excel服务 ===")
    excel_service = get_excel_service()
    
    test_data = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "industry": "测试行业",
        "title": "测试标题",
        "summary": "测试摘要内容",
        "source_url": "https://example.com",
        "category": "动态",
        "importance": "中",
        "keywords": ["测试", "关键词"]
    }
    
    try:
        excel_service.save_intelligence(test_data)
        print(f"✓ Excel写入成功")
        
        # 验证文件是否创建
        data_dir = Path(settings.excel_dir)
        excel_files = list(data_dir.glob("intelligence_*.xlsx"))
        if excel_files:
            print(f"  Excel文件: {excel_files[0].name}")
        return True
    except Exception as e:
        print(f"✗ Excel写入失败: {e}")
        return False


async def test_feishu_push():
    """测试飞书推送服务"""
    print("\n=== 测试飞书推送服务 ===")
    
    if not settings.feishu_webhook_url:
        print("⚠ 未配置飞书Webhook，跳过测试")
        return None
    
    feishu_service = get_notification_service()
    
    test_intelligences = [
        {
            "industry": "测试行业",
            "title": "系统功能测试消息",
            "summary": "这是一条系统测试消息，用于验证飞书推送功能是否正常。",
            "source_url": "https://example.com",
            "category": "动态",
            "importance": "中"
        }
    ]
    
    try:
        await feishu_service.send_daily_report(
            datetime.now().strftime("%Y-%m-%d"),
            test_intelligences
        )
        print(f"✓ 飞书推送成功（请检查群聊是否收到消息）")
        return True
    except Exception as e:
        print(f"✗ 飞书推送失败: {e}")
        return False


async def test_full_pipeline():
    """测试完整采集流程"""
    print("\n=== 测试完整采集流程 ===")
    
    # 加载行业配置
    config_path = Path("config.json")
    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)
    
    # 只测试第一个启用的行业
    test_industry = None
    for industry in config["industries"]:
        if industry["enabled"]:
            test_industry = industry
            break
    
    if not test_industry:
        print("✗ 没有启用的行业配置")
        return False
    
    print(f"测试行业: {test_industry['name']}")
    print(f"关键词: {test_industry['keywords'][:3]}...")
    
    search_service = get_search_service()
    ai_service = get_ai_service()
    excel_service = get_excel_service()
    
    all_intelligences = []
    
    # 搜索（只取前2个关键词以节省时间）
    for keyword in test_industry["keywords"][:2]:
        try:
            results = await search_service.search(keyword, max_results=3)
            print(f"  关键词 '{keyword}': {len(results)} 条结果")
            
            if results:
                # AI总结
                summary = await ai_service.summarize_articles(
                    test_industry["name"],
                    results
                )
                all_intelligences.append(summary)
                
        except Exception as e:
            print(f"  关键词 '{keyword}' 处理失败: {e}")
    
    if all_intelligences:
        print(f"\n✓ 共生成 {len(all_intelligences)} 条情报")
        
        # 保存到Excel
        for intel in all_intelligences:
            intel["date"] = datetime.now().strftime("%Y-%m-%d")
            excel_service.save_intelligence(intel)
        
        print(f"✓ 已保存到Excel")
        
        # 推送到飞书（可选）
        if settings.feishu_webhook_url:
            feishu_service = get_notification_service()
            try:
                await feishu_service.send_daily_report(
                    datetime.now().strftime("%Y-%m-%d"),
                    all_intelligences
                )
                print(f"✓ 已推送到飞书")
            except Exception as e:
                print(f"⚠ 飞书推送失败: {e}")
        
        return True
    else:
        print("✗ 未生成任何情报")
        return False


async def main():
    """运行所有测试"""
    print("=" * 60)
    print("AI行业情报系统 - 功能测试")
    print("=" * 60)
    print(f"\n配置信息:")
    print(f"  AI Provider: {settings.ai_provider}")
    print(f"  数据目录: {settings.excel_dir}")
    print(f"  定时时间: {settings.schedule_times_list}")
    print(f"  时区: {settings.timezone}")
    
    results = {}
    
    # 单元测试
    results["搜索服务"] = await test_search()
    results["AI总结服务"] = await test_ai_summary()
    results["Excel服务"] = test_excel_service()
    results["飞书推送"] = await test_feishu_push()
    
    # 集成测试
    results["完整流程"] = await test_full_pipeline()
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)
    
    for test_name, result in results.items():
        if result is True:
            status = "✓ 通过"
        elif result is False:
            status = "✗ 失败"
        else:
            status = "⊙ 跳过"
        print(f"{test_name:12s}: {status}")
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    
    print(f"\n通过: {passed} | 失败: {failed} | 跳过: {skipped}")
    
    if failed == 0 and passed > 0:
        print("\n🎉 所有测试通过！系统运行正常。")
    elif failed > 0:
        print(f"\n⚠ 有 {failed} 个测试失败，请检查配置和日志。")


if __name__ == "__main__":
    asyncio.run(main())