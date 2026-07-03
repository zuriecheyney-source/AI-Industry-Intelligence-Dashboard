from typing import List, Dict, Any, Optional
import logging
import json
import re

from app.core.ai_client import generate_text
from app.models.intelligence import IntelligenceCategory, ImportanceLevel

logger = logging.getLogger(__name__)


class AIAnalysisService:
    """AI分析服务"""
    
    SYSTEM_PROMPT = """你是一个专业的行业情报分析师。你的任务是：
1. 分析新闻标题和摘要，提取关键信息
2. 判断情报的分类（政策/竞品/研报/动态）
3. 评估情报的重要程度（高/中/低）
4. 生成简洁准确的中文摘要（100-150字）
5. 提取关键词（3-5个）

你必须以JSON格式输出结果。"""
    
    ANALYSIS_PROMPT_TEMPLATE = """请分析以下{industry}领域的情报：

标题：{title}
内容摘要：{snippet}
来源：{source}

请按以下JSON格式输出分析结果：
{{
    "category": "政策|竞品|研报|动态",
    "importance": "高|中|低",
    "summary": "100-150字的中文摘要",
    "keywords": ["关键词1", "关键词2", "关键词3"]
}}

分类判断标准：
- 政策：政府政策、法规、监管文件
- 竞品：竞争对手动态、产品发布、战略调整
- 研报：行业报告、市场分析、趋势预测
- 动态：行业新闻、技术突破、市场变化

重要程度判断：
- 高：重大政策发布、行业颠覆性事件、重要竞品动作
- 中：一般性政策调整、常规行业动态、普通产品更新
- 低：次要新闻、边缘信息、非核心动态

只输出JSON，不要有其他内容。"""
    
    async def analyze_intelligence(
        self,
        title: str,
        snippet: str,
        source: str,
        industry: str
    ) -> Dict[str, Any]:
        """分析单条情报"""
        
        prompt = self.ANALYSIS_PROMPT_TEMPLATE.format(
            industry=industry,
            title=title,
            snippet=snippet,
            source=source or "未知来源"
        )
        
        try:
            response = await generate_text(
                prompt=prompt,
                system_prompt=self.SYSTEM_PROMPT
            )
            
            # 提取JSON内容
            json_text = self._extract_json(response)
            analysis = json.loads(json_text)
            
            # 验证和规范化输出
            return {
                "category": self._normalize_category(analysis.get("category", "动态")),
                "importance": self._normalize_importance(analysis.get("importance", "中")),
                "summary": analysis.get("summary", snippet)[:200],  # 限制长度
                "keywords": analysis.get("keywords", [])[:5]  # 最多5个关键词
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"AI返回的JSON解析失败: {str(e)}, 原始响应: {response[:200]}")
            return self._fallback_analysis(title, snippet)
        
        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
            return self._fallback_analysis(title, snippet)
    
    def _extract_json(self, text: str) -> str:
        """从文本中提取JSON内容"""
        # 尝试找到JSON代码块
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
        if json_match:
            return json_match.group(1)
        
        # 尝试直接找到JSON对象
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json_match.group(0)
        
        return text
    
    def _normalize_category(self, category: str) -> str:
        """规范化分类"""
        category_map = {
            "政策": IntelligenceCategory.POLICY.value,
            "竞品": IntelligenceCategory.COMPETITOR.value,
            "研报": IntelligenceCategory.REPORT.value,
            "动态": IntelligenceCategory.NEWS.value,
        }
        return category_map.get(category, IntelligenceCategory.NEWS.value)
    
    def _normalize_importance(self, importance: str) -> str:
        """规范化重要程度"""
        importance_map = {
            "高": ImportanceLevel.HIGH.value,
            "中": ImportanceLevel.MEDIUM.value,
            "低": ImportanceLevel.LOW.value,
        }
        return importance_map.get(importance, ImportanceLevel.MEDIUM.value)
    
    def _fallback_analysis(self, title: str, snippet: str) -> Dict[str, Any]:
        """备用分析（当AI失败时）"""
        # 简单的关键词提取
        keywords = self._extract_keywords_simple(title + " " + snippet)
        
        # 简单的分类判断
        category = self._classify_simple(title + " " + snippet)
        
        return {
            "category": category,
            "importance": ImportanceLevel.MEDIUM.value,
            "summary": snippet[:150],
            "keywords": keywords
        }
    
    def _extract_keywords_simple(self, text: str) -> List[str]:
        """简单的关键词提取"""
        # 这里可以使用jieba等分词工具，暂时简化处理
        keywords = []
        
        # 预定义的关键词库
        keyword_patterns = [
            "人工智能", "AI", "大模型", "ChatGPT", "机器学习",
            "房地产", "楼市", "房价", "政策",
            "金融", "银行", "证券", "基金", "股市",
            "发布", "上线", "推出", "合作", "融资"
        ]
        
        for keyword in keyword_patterns:
            if keyword in text:
                keywords.append(keyword)
                if len(keywords) >= 5:
                    break
        
        return keywords[:5]
    
    def _classify_simple(self, text: str) -> str:
        """简单的分类判断"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ["政策", "法规", "监管", "通知", "文件"]):
            return IntelligenceCategory.POLICY.value
        elif any(word in text_lower for word in ["报告", "研报", "预测", "分析", "趋势"]):
            return IntelligenceCategory.REPORT.value
        elif any(word in text_lower for word in ["竞争", "对手", "战略", "市场份额"]):
            return IntelligenceCategory.COMPETITOR.value
        else:
            return IntelligenceCategory.NEWS.value
    
    async def batch_analyze(
        self,
        search_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """批量分析情报"""
        analyzed_results = []
        
        for result in search_results:
            try:
                analysis = await self.analyze_intelligence(
                    title=result["title"],
                    snippet=result["snippet"],
                    source=result.get("source", ""),
                    industry=result["industry"]
                )
                
                # 合并分析结果
                intelligence = {
                    **result,
                    **analysis
                }
                
                analyzed_results.append(intelligence)
                
            except Exception as e:
                logger.error(f"批量分析失败 - 标题: {result.get('title', '')[:50]}, 错误: {str(e)}")
                continue
        
        logger.info(f"批量分析完成: {len(analyzed_results)}/{len(search_results)} 条成功")
        return analyzed_results


# 单例实例
_ai_service_instance = None

def get_ai_service() -> AIAnalysisService:
    """获取AI服务单例"""
    global _ai_service_instance
    if _ai_service_instance is None:
        _ai_service_instance = AIAnalysisService()
    return _ai_service_instance