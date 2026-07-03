from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from datetime import date as date_type
from enum import Enum


class IntelligenceCategory(str, Enum):
    """情报分类"""
    POLICY = "政策"
    COMPETITOR = "竞品"
    REPORT = "研报"
    NEWS = "动态"


class ImportanceLevel(str, Enum):
    """重要程度"""
    HIGH = "高"
    MEDIUM = "中"
    LOW = "低"


class Intelligence(BaseModel):
    """情报数据模型"""
    id: Optional[str] = None
    date: date_type = Field(default_factory=lambda: datetime.now().date())
    industry: str = Field(..., description="所属行业")
    title: str = Field(..., description="情报标题")
    summary: str = Field(..., description="情报摘要")
    source_url: str = Field(..., description="来源链接")
    source_name: Optional[str] = Field(None, description="来源名称")
    category: IntelligenceCategory = Field(..., description="情报分类")
    importance: ImportanceLevel = Field(ImportanceLevel.MEDIUM, description="重要程度")
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    created_at: datetime = Field(default_factory=datetime.now)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "industry": "AI板块",
                "title": "DeepSeek发布新一代模型，性能提升40%",
                "summary": "DeepSeek今日正式发布新模型，在推理能力、多模态理解等方面较上一代提升40%。新模型支持更长的上下文窗口，并优化了成本结构。",
                "source_url": "https://example.com/news/123",
                "source_name": "AI前线",
                "category": "政策红利",
                "importance": "high",
                "keywords": ["DeepSeek", "大模型"]
            }
        }
    )


class IndustryConfig(BaseModel):
    """行业配置模型"""
    name: str = Field(..., description="行业名称")
    keywords: List[str] = Field(..., description="关键词列表")
    enabled: bool = Field(True, description="是否启用")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "name": "AI板块",
                "keywords": ["人工智能", "大模型", "ChatGPT", "AI芯片"],
                "enabled": True
            }
        }
    )


class IntelligenceQuery(BaseModel):
    """情报查询参数"""
    industry: Optional[str] = None
    category: Optional[IntelligenceCategory] = None
    importance: Optional[ImportanceLevel] = None
    start_date: Optional[date_type] = None
    end_date: Optional[date_type] = None
    keyword: Optional[str] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class IntelligenceResponse(BaseModel):
    """情报查询响应"""
    total: int
    page: int
    page_size: int
    items: List[Intelligence]


class TaskStatus(BaseModel):
    """任务状态"""
    task_id: str
    status: str  # running, completed, failed
    message: str
    start_time: datetime
    end_time: Optional[datetime] = None
    intelligence_count: int = 0