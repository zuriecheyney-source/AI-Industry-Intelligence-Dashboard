"""综合测试脚本 - 诊断问题并测试完整流程"""
import asyncio
import json
import sys
import os
from datetime import datetime
from pathlib import Path

# 设置 UTF-8 输出（Windows 控制台兼容）
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    # 尝试设置控制台代码页为 UTF-8
    try:
        os.system('chcp 65001 >nul 2>&1')
    except:
        pass

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from app.core.config import settings
from app.services.search_service import get_search_service
from app.services.ai_service import get_ai_service
from app.services.excel_service import get_excel_service
from app.services.notification_service import get_notification_service
from app.models.intelligence import Intelligence


def print_header(title):
    """打印标题"""
    print(f"\n{'=' * 60}")
    print(f"{title:^60}")
    print(f"{'=' * 60}\n")


def print_section(title):
    """打印小节标题"""
    print(f"\n{'-' * 60}")
    print(f"  {title}")
    print(f"{'-' * 60}")


async def test_api_connectivity():
    """测试各 API 连接性"""
    print_section("1. API 连接性测试")
    
    results = {}
    
    # 测试 Serper API
    print("\n[1/3] 测试 Serper API...")
    if not settings.serper_api_key:
        print("  ✗ 未配置 SERPER_API_KEY")
        results['serper'] = False
    else:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    "https://google.serper.dev/search",
                    headers={
                        "X-API-KEY": settings.serper_api_key,
                        "Content-Type": "application/json"
                    },
                    json={"q": "test", "num": 1}
                )
                if response.status_code == 200:
                    print(f"  ✓ Serper API 连接正常")
                    results['serper'] = True
                elif response.status_code == 403:
                    print(f"  ✗ Serper API 返回 403 - API Key 无效或已过期")
                    print(f"    提示：请访问 https://serper.dev 获取新的 API Key")
                    results['serper'] = False
                else:
                    print(f"  ✗ Serper API 返回 {response.status_code}")
                    results['serper'] = False
        except Exception as e:
            print(f"  ✗ Serper API 连接失败: {e}")
            results['serper'] = False
    
    # 测试 AI API
    print("\n[2/3] 测试 AI API...")
    ai_service = get_ai_service()
    try:
        # 使用一个简单的分析任务来测试 AI API
        test_result = await ai_service.analyze_intelligence(
            title="测试标题",
            snippet="测试内容",
            source="测试来源",
            industry="测试行业"
        )
        print(f"  ✓ AI API ({settings.ai_provider}) 连接正常")
        results['ai'] = True
    except Exception as e:
        print(f"  ✗ AI API 连接失败: {e}")
        results['ai'] = False
    
    # 测试飞书 Webhook
    print("\n[3/3] 测试飞书 Webhook...")
    if not settings.feishu_webhook_url:
        print("  ⊙ 未配置 FEISHU_WEBHOOK_URL，跳过")
        results['feishu'] = None
    else:
        try:
            import httpx
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(
                    settings.feishu_webhook_url,
                    json={
                        "msg_type": "text",
                        "content": {"text": "测试连接"}
                    }
                )
                if response.status_code == 200:
                    data = response.json()
                    if data.get("code") == 0:
                        print(f"  ✓ 飞书 Webhook 连接正常")
                        results['feishu'] = True
                    else:
                        print(f"  ✗ 飞书 Webhook 返回错误: {data}")
                        results['feishu'] = False
                else:
                    print(f"  ✗ 飞书 Webhook 返回 {response.status_code}")
                    results['feishu'] = False
        except Exception as e:
            print(f"  ✗ 飞书 Webhook 连接失败: {e}")
            results['feishu'] = False
    
    return results


async def test_with_mock_data():
    """使用模拟数据测试完整流程"""
    print_section("2. 使用模拟数据测试完整流程")
    
    # 模拟搜索结果
    mock_search_results = [
        {
            "title": "DeepSeek 发布新模型，性能提升 40%",
            "snippet": "DeepSeek 今日宣布推出最新一代大语言模型，在多个基准测试中表现优异，相比上一代性能提升约 40%。新模型支持更长的上下文窗口，并改进了推理能力。",
            "link": "https://example.com/gpt5-release",
            "source": "TechCrunch"
        },
        {
            "title": "百度文心大模型 4.0 正式上线",
            "snippet": "百度今天发布了文心大模型 4.0 版本，新增了多模态理解能力，支持图文混合输入。该模型在中文理解和生成任务上表现出色。",
            "link": "https://example.com/wenxin-4.0",
            "source": "36氪"
        },
        {
            "title": "AI 芯片市场规模预计 2025 年突破千亿美元",
            "snippet": "根据最新市场研究报告，全球 AI 芯片市场规模预计在 2025 年突破 1000 亿美元，年复合增长率达 35%。英伟达、AMD 和国内厂商竞争激烈。",
            "link": "https://example.com/ai-chip-market",
            "source": "IDC"
        }
    ]
    
    print("\n✓ 模拟搜索结果：3 条")
    for i, result in enumerate(mock_search_results, 1):
        print(f"  {i}. {result['title'][:40]}...")
    
    # 测试 AI 总结
    print("\n[测试 AI 总结服务]")
    ai_service = get_ai_service()
    try:
        # 使用第一条模拟数据进行测试
        first_result = mock_search_results[0]
        intelligence = await ai_service.analyze_intelligence(
            title=first_result['title'],
            snippet=first_result['snippet'],
            source=first_result['source'],
            industry="AI板块"
        )
        print(f"  ✓ AI 总结成功")
        print(f"    分类: {intelligence['category']}")
        print(f"    重要度: {intelligence['importance']}")
        print(f"    关键词: {', '.join(intelligence['keywords'])}")
        print(f"    摘要: {intelligence['summary'][:100]}...")
        
        # 组合成完整情报数据
        intelligence.update({
            'title': first_result['title'],
            'source_url': first_result['link'],
            'industry': 'AI板块'
        })
    except Exception as e:
        print(f"  ✗ AI 总结失败: {e}")
        return False
    
    # 测试 Excel 保存
    print("\n[测试 Excel 保存]")
    excel_service = get_excel_service()
    try:
        # 转换为 Intelligence 模型
        intel_model = Intelligence(**intelligence)
        excel_service.save_intelligence(intel_model)
        print(f"  ✓ Excel 保存成功")
        
        # 验证文件
        data_dir = Path(settings.excel_dir)
        excel_files = list(data_dir.glob("intelligence_*.xlsx"))
        if excel_files:
            print(f"    文件: {excel_files[0].name}")
    except Exception as e:
        print(f"  ✗ Excel 保存失败: {e}")
        return False
    
    # 测试飞书推送
    print("\n[测试飞书推送]")
    if not settings.feishu_webhook_url:
        print("  ⊙ 未配置飞书 Webhook，跳过推送测试")
    else:
        feishu_service = get_notification_service()
        try:
            # 转换为 Intelligence 模型并按行业分组
            intel_model = Intelligence(**intelligence)
            grouped = {"AI板块": [intel_model]}
            await feishu_service.send_daily_intelligence(
                intelligence_by_industry=grouped,
                send_date=datetime.now()
            )
            print(f"  ✓ 飞书推送成功（请检查群聊消息）")
        except Exception as e:
            print(f"  ✗ 飞书推送失败: {e}")
    
    return True


def test_configuration():
    """测试配置文件"""
    print_section("3. 配置文件检查")
    
    results = {}
    
    # 检查 .env 配置
    print("\n[检查环境变量]")
    configs = {
        "AI_PROVIDER": settings.ai_provider,
        "SERPER_API_KEY": "已配置" if settings.serper_api_key else "未配置",
        "FEISHU_WEBHOOK_URL": "已配置" if settings.feishu_webhook_url else "未配置",
        "EXCEL_DIR": settings.excel_dir,
        "SCHEDULE_TIMES": ", ".join(settings.schedule_times_list),
        "TIMEZONE": settings.timezone
    }
    
    for key, value in configs.items():
        print(f"  {key}: {value}")
    
    # 检查 config.json
    print("\n[检查行业配置]")
    config_path = Path("config.json")
    if not config_path.exists():
        print("  ✗ config.json 不存在")
        results['config'] = False
    else:
        try:
            with open(config_path, encoding="utf-8") as f:
                config = json.load(f)
            
            industries = config.get("industries", [])
            enabled_count = sum(1 for ind in industries if ind.get("enabled"))
            
            print(f"  ✓ 配置文件正常")
            print(f"    总行业数: {len(industries)}")
            print(f"    启用行业: {enabled_count}")
            
            for ind in industries[:3]:  # 只显示前3个
                status = "✓" if ind.get("enabled") else "○"
                print(f"    {status} {ind['name']}: {len(ind.get('keywords', []))} 个关键词")
            
            results['config'] = True
        except Exception as e:
            print(f"  ✗ 配置文件解析失败: {e}")
            results['config'] = False
    
    # 检查数据目录
    print("\n[检查数据目录]")
    data_dir = Path(settings.excel_dir)
    if not data_dir.exists():
        print(f"  ⚠ 数据目录不存在，创建: {data_dir}")
        data_dir.mkdir(parents=True, exist_ok=True)
    
    excel_files = list(data_dir.glob("intelligence_*.xlsx"))
    print(f"  ✓ 数据目录: {data_dir}")
    print(f"    Excel 文件数: {len(excel_files)}")
    
    return results


async def main():
    """运行所有测试"""
    print_header("AI 行业情报系统 - 综合测试")
    
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python: {sys.version.split()[0]}")
    
    # 1. 配置检查
    config_results = test_configuration()
    
    # 2. API 连接性测试
    api_results = await test_api_connectivity()
    
    # 3. 模拟数据流程测试
    mock_test_passed = await test_with_mock_data()
    
    # 汇总结果
    print_header("测试结果汇总")
    
    print("\n[API 连接性]")
    for api, result in api_results.items():
        if result is True:
            status = "✓ 正常"
        elif result is False:
            status = "✗ 失败"
        else:
            status = "⊙ 跳过"
        print(f"  {api:15s}: {status}")
    
    print("\n[配置检查]")
    for key, result in config_results.items():
        status = "✓ 正常" if result else "✗ 失败"
        print(f"  {key:15s}: {status}")
    
    print("\n[完整流程]")
    status = "✓ 通过" if mock_test_passed else "✗ 失败"
    print(f"  模拟数据测试  : {status}")
    
    # 诊断建议
    print_header("诊断建议")
    
    if not api_results.get('serper'):
        print("\n⚠ Serper API 不可用")
        print("  问题: 这是导致系统无法采集数据的主要原因")
        print("  解决方案:")
        print("    1. 访问 https://serper.dev 注册账号")
        print("    2. 获取新的 API Key（免费额度 2500 次/月）")
        print("    3. 更新 backend/.env 中的 SERPER_API_KEY")
        print("    4. 重启后端服务")
    
    if not api_results.get('ai'):
        print("\n⚠ AI API 不可用")
        print("  问题: 无法进行情报总结")
        print("  解决方案:")
        print("    1. 检查 backend/.env 中的 AI API 配置")
        print("    2. 确认 API Key 有效且有余额")
        print("    3. 尝试切换到其他 AI Provider")
    
    if mock_test_passed and not api_results.get('serper'):
        print("\n✓ 好消息")
        print("  系统其他组件工作正常（AI 总结、Excel 保存、飞书推送）")
        print("  只需要解决 Serper API 问题即可正常使用")
    
    if mock_test_passed and api_results.get('serper'):
        print("\n🎉 系统完全正常")
        print("  所有组件测试通过，可以开始采集情报")
        print("  手动触发: 浏览器访问 http://127.0.0.1:8000/docs")
        print("  或等待定时任务: 每日 " + ", ".join(settings.schedule_times_list))
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n测试被中断")
    except Exception as e:
        print(f"\n\n✗ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()