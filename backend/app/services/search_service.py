import httpx
from typing import List, Dict, Optional, Any
from datetime import datetime, timedelta
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class SearchResult:
    """搜索结果"""
    def __init__(self, title: str, link: str, snippet: str, source: str = ""):
        self.title = title
        self.link = link
        self.snippet = snippet
        self.source = source
        self.timestamp = datetime.now()


class SearchServiceBase:
    """搜索服务基类"""
    
    async def search(self, query: str, num_results: int = 5, 
                    date_range_days: int = 1) -> List[SearchResult]:
        """搜索"""
        raise NotImplementedError


class SerperSearchService(SearchServiceBase):
    """Serper API搜索服务"""
    
    def __init__(self):
        self.api_key = settings.serper_api_key
        self.base_url = "https://google.serper.dev/search"
    
    async def search(self, query: str, num_results: int = 5,
                    date_range_days: int = 1) -> List[SearchResult]:
        """使用Serper API搜索"""
        if not self.api_key:
            raise ValueError("Serper API密钥未配置")
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
        
        # 构建搜索参数
        payload = {
            "q": query,
            "num": num_results,
            "gl": "cn",  # 地理位置：中国
            "hl": "zh-cn"  # 语言：简体中文
        }
        
        # 添加时间范围
        if date_range_days > 0:
            payload["tbs"] = f"qdr:d{date_range_days}"  # 最近N天
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.base_url,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("organic", [])[:num_results]:
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        link=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        source=item.get("source", "")
                    ))
                
                logger.info(f"Serper搜索完成: {query}, 结果数: {len(results)}")
                return results
                
        except Exception as e:
            logger.error(f"Serper搜索失败: {query}, 错误: {str(e)}")
            return []


class GoogleSearchService(SearchServiceBase):
    """Google Custom Search API服务"""
    
    def __init__(self):
        self.api_key = settings.google_search_api_key
        self.engine_id = settings.google_search_engine_id
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    async def search(self, query: str, num_results: int = 5,
                    date_range_days: int = 1) -> List[SearchResult]:
        """使用Google Custom Search API搜索"""
        if not self.api_key or not self.engine_id:
            raise ValueError("Google Search API密钥或引擎ID未配置")
        
        params = {
            "key": self.api_key,
            "cx": self.engine_id,
            "q": query,
            "num": min(num_results, 10),  # Google限制每次最多10条
            "lr": "lang_zh-CN"
        }
        
        # 添加时间范围
        if date_range_days == 1:
            params["dateRestrict"] = "d1"
        elif date_range_days <= 7:
            params["dateRestrict"] = f"d{date_range_days}"
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(self.base_url, params=params)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("items", [])[:num_results]:
                    results.append(SearchResult(
                        title=item.get("title", ""),
                        link=item.get("link", ""),
                        snippet=item.get("snippet", ""),
                        source=item.get("displayLink", "")
                    ))
                
                logger.info(f"Google搜索完成: {query}, 结果数: {len(results)}")
                return results
                
        except Exception as e:
            logger.error(f"Google搜索失败: {query}, 错误: {str(e)}")
            return []


class BingSearchService(SearchServiceBase):
    """Bing Search API服务"""
    
    def __init__(self):
        self.api_key = settings.bing_search_api_key
        self.base_url = "https://api.bing.microsoft.com/v7.0/search"
    
    async def search(self, query: str, num_results: int = 5,
                    date_range_days: int = 1) -> List[SearchResult]:
        """使用Bing Search API搜索"""
        if not self.api_key:
            raise ValueError("Bing Search API密钥未配置")
        
        headers = {
            "Ocp-Apim-Subscription-Key": self.api_key
        }
        
        params = {
            "q": query,
            "count": num_results,
            "mkt": "zh-CN",
            "freshness": "Day" if date_range_days == 1 else "Week"
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    self.base_url,
                    headers=headers,
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("webPages", {}).get("value", [])[:num_results]:
                    results.append(SearchResult(
                        title=item.get("name", ""),
                        link=item.get("url", ""),
                        snippet=item.get("snippet", ""),
                        source=""
                    ))
                
                logger.info(f"Bing搜索完成: {query}, 结果数: {len(results)}")
                return results
                
        except Exception as e:
            logger.error(f"Bing搜索失败: {query}, 错误: {str(e)}")
            return []


class IntelligenceSearchService:
    """情报搜索服务（高层封装）"""
    
    def __init__(self):
        self._init_search_service()
    
    def _init_search_service(self):
        """初始化搜索服务"""
        if settings.serper_api_key:
            self.search_service = SerperSearchService()
            logger.info("使用Serper搜索服务")
        elif settings.google_search_api_key and settings.google_search_engine_id:
            self.search_service = GoogleSearchService()
            logger.info("使用Google搜索服务")
        elif settings.bing_search_api_key:
            self.search_service = BingSearchService()
            logger.info("使用Bing搜索服务")
        else:
            raise ValueError("未配置任何搜索API，请在.env中配置SERPER_API_KEY或其他搜索API")
    
    async def search_industry_intelligence(
        self,
        industry: str,
        keywords: List[str],
        max_results_per_keyword: int = 5,
        date_range_days: int = 1
    ) -> List[Dict[str, Any]]:
        """搜索行业情报"""
        all_results = []
        seen_urls = set()
        
        for keyword in keywords:
            # 构建搜索查询
            query = f"{industry} {keyword} 最新"
            
            try:
                results = await self.search_service.search(
                    query=query,
                    num_results=max_results_per_keyword,
                    date_range_days=date_range_days
                )
                
                # 去重并收集结果
                for result in results:
                    if result.link not in seen_urls:
                        seen_urls.add(result.link)
                        all_results.append({
                            "industry": industry,
                            "keyword": keyword,
                            "title": result.title,
                            "url": result.link,
                            "snippet": result.snippet,
                            "source": result.source,
                            "timestamp": result.timestamp.isoformat()
                        })
            
            except Exception as e:
                logger.error(f"搜索失败 - 行业: {industry}, 关键词: {keyword}, 错误: {str(e)}")
                continue
        
        logger.info(f"行业情报搜索完成 - {industry}: 共{len(all_results)}条结果")
        return all_results
    
    async def search_multiple_industries(
        self,
        industry_configs: List[Dict[str, Any]],
        max_results_per_keyword: int = 5,
        date_range_days: int = 1
    ) -> Dict[str, List[Dict[str, Any]]]:
        """批量搜索多个行业的情报"""
        results_by_industry = {}
        
        for config in industry_configs:
            if not config.get("enabled", True):
                continue
            
            industry = config["name"]
            keywords = config["keywords"]
            
            results = await self.search_industry_intelligence(
                industry=industry,
                keywords=keywords,
                max_results_per_keyword=max_results_per_keyword,
                date_range_days=date_range_days
            )
            
            results_by_industry[industry] = results
        
        total_results = sum(len(r) for r in results_by_industry.values())
        logger.info(f"多行业搜索完成: {len(results_by_industry)}个行业, 共{total_results}条结果")
        
        return results_by_industry


# 单例实例
_search_service_instance = None

def get_search_service() -> IntelligenceSearchService:
    """获取搜索服务单例"""
    global _search_service_instance
    if _search_service_instance is None:
        _search_service_instance = IntelligenceSearchService()
    return _search_service_instance