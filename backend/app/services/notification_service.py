import httpx
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from app.core.config import settings
from app.models.intelligence import Intelligence, ImportanceLevel

logger = logging.getLogger(__name__)


class FeishuNotificationService:
    """飞书通知服务"""
    
    def __init__(self):
        self.webhook_url = settings.feishu_webhook_url
    
    def _format_intelligence_message(
        self,
        intelligence_by_industry: Dict[str, List[Intelligence]],
        date_str: str
    ) -> str:
        """格式化情报消息"""
        
        # 表情符号映射
        industry_emoji = {
            "AI板块": "🔥",
            "房地产政策": "🏠",
            "金融板块": "💰",
        }
        
        importance_emoji = {
            ImportanceLevel.HIGH.value: "🔴",
            ImportanceLevel.MEDIUM.value: "🟡",
            ImportanceLevel.LOW.value: "🟢",
        }
        
        # 构建消息
        lines = [f"【AI行业情报 - {date_str}】\n"]
        
        total_count = sum(len(items) for items in intelligence_by_industry.values())
        
        for industry, items in intelligence_by_industry.items():
            if not items:
                continue
            
            emoji = industry_emoji.get(industry, "📊")
            lines.append(f"{emoji} {industry}（{len(items)}条）")
            lines.append("━━━━━━━━━━━━━━━")
            
            for intel in items[:5]:  # 每个行业最多展示5条
                importance_icon = importance_emoji.get(intel.importance, "")
                lines.append(f"{importance_icon} 📌 {intel.title}")
                lines.append(f"   🔗 来源：{intel.source_name or '未知'}")
                
                # 摘要限制在100字内
                summary = intel.summary[:100] + "..." if len(intel.summary) > 100 else intel.summary
                lines.append(f"   💡 {summary}")
                lines.append("")
            
            if len(items) > 5:
                lines.append(f"   ... 还有 {len(items) - 5} 条情报")
            
            lines.append("")
        
        # 添加查看详情链接
        if settings.frontend_url:
            lines.append(f"查看详情：{settings.frontend_url}")
        
        return "\n".join(lines)
    
    async def send_text_message(self, content: str) -> bool:
        """发送文本消息"""
        if not self.webhook_url:
            logger.warning("飞书Webhook未配置，跳过发送")
            return False
        
        payload = {
            "msg_type": "text",
            "content": {
                "text": content
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(self.webhook_url, json=payload)
                response.raise_for_status()
                result = response.json()
                
                if result.get("code") == 0:
                    logger.info("飞书消息发送成功")
                    return True
                else:
                    logger.error(f"飞书消息发送失败: {result}")
                    return False
                    
        except Exception as e:
            logger.error(f"发送飞书消息异常: {str(e)}")
            return False
    
    async def send_daily_intelligence(
        self,
        intelligence_by_industry: Dict[str, List[Intelligence]],
        send_date: Optional[datetime] = None
    ) -> bool:
        """发送每日情报汇总"""
        
        date_str = (send_date or datetime.now()).strftime("%Y-%m-%d")
        
        # 按行业分组
        grouped: Dict[str, List[Intelligence]] = {}
        for industry, items in intelligence_by_industry.items():
            if items:
                grouped[industry] = items
        
        if not grouped:
            logger.info("没有情报需要推送")
            return False
        
        # 格式化消息
        message = self._format_intelligence_message(grouped, date_str)
        
        # 发送文本消息
        success = await self.send_text_message(message)
        
        return success
    
    async def send_urgent_intelligence(self, intelligence: Intelligence) -> bool:
        """发送紧急情报（重要程度为高的情报）"""
        
        if intelligence.importance != ImportanceLevel.HIGH.value:
            return False
        
        message = f"""【🔴 重要情报提醒】

行业：{intelligence.industry}
标题：{intelligence.title}

摘要：{intelligence.summary}

来源：{intelligence.source_name or '未知'}
链接：{intelligence.source_url}

分类：{intelligence.category}
关键词：{', '.join(intelligence.keywords)}
"""
        
        return await self.send_text_message(message)
    
    async def send_test_message(self) -> bool:
        """发送测试消息"""
        test_message = f"""【测试消息】

AI行业情报系统运行正常

时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
配置的AI提供商：{settings.ai_provider}

此消息用于测试飞书推送功能。"""
        
        return await self.send_text_message(test_message)


# 单例实例
_feishu_service_instance = None

def get_notification_service() -> FeishuNotificationService:
    """获取通知服务单例"""
    global _feishu_service_instance
    if _feishu_service_instance is None:
        _feishu_service_instance = FeishuNotificationService()
    return _feishu_service_instance