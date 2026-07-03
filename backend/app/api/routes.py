from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Optional, List
from datetime import date, datetime
import json
from pathlib import Path

from app.models.intelligence import (
    IndustryConfig,
    IntelligenceQuery,
    IntelligenceResponse,
    Intelligence,
    TaskStatus
)
from app.services.excel_service import get_excel_service
from app.scheduler.tasks import (
    trigger_manual_collection,
    get_scheduler_status
)
from app.services.notification_service import get_notification_service
from app.core.config import settings

router = APIRouter()


# ==================== 情报查询接口 ====================

@router.get("/intelligence", response_model=IntelligenceResponse)
async def get_intelligence_list(
    industry: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    keyword: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """
    查询情报列表
    
    - **industry**: 行业筛选
    - **start_date**: 开始日期 (YYYY-MM-DD)
    - **end_date**: 结束日期 (YYYY-MM-DD)
    - **keyword**: 关键词搜索
    - **page**: 页码（从1开始）
    - **page_size**: 每页数量
    """
    excel_service = get_excel_service()
    
    # 解析日期
    if not start_date:
        start_date = datetime.now().replace(day=1).date()
    else:
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    
    if not end_date:
        end_date = datetime.now().date()
    else:
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
    
    # 加载数据
    results = excel_service.load_intelligence_by_date_range(
        start_date=start_date,
        end_date=end_date,
        industry=industry
    )
    
    # 关键词过滤
    if keyword:
        keyword_lower = keyword.lower()
        results = [
            r for r in results
            if keyword_lower in r.get("标题", "").lower() 
            or keyword_lower in r.get("摘要", "").lower()
        ]
    
    # 分页
    total = len(results)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    page_results = results[start_idx:end_idx]
    
    # 转换为Intelligence对象
    items = []
    for r in page_results:
        try:
            # 处理枚举字符串（Excel 可能存储为 "IntelligenceCategory.NEWS" 形式）
            category = r["分类"]
            if "." in str(category):
                category = str(category).split(".")[-1].lower()
                category_map = {"news": "动态", "policy": "政策", "competitor": "竞品", "report": "研报"}
                category = category_map.get(category, "动态")
            
            importance = r["重要度"]
            if "." in str(importance):
                importance = str(importance).split(".")[-1].lower()
                importance_map = {"high": "高", "medium": "中", "low": "低"}
                importance = importance_map.get(importance, "中")
            
            items.append(Intelligence(
                date=datetime.strptime(r["日期"], "%Y-%m-%d").date(),
                industry=r["行业"],
                title=r["标题"],
                summary=r["摘要"],
                source_url=r["URL"],
                source_name=r["来源"],
                category=category,
                importance=importance,
                keywords=r["关键词"].split(", ") if r.get("关键词") else []
            ))
        except Exception as e:
            continue
    
    return IntelligenceResponse(
        total=total,
        page=page,
        page_size=page_size,
        items=items
    )


@router.get("/intelligence/statistics")
async def get_intelligence_statistics():
    """获取情报统计信息"""
    excel_service = get_excel_service()
    stats = excel_service.get_statistics()
    return stats


# ==================== 行业配置接口 ====================

@router.get("/industries", response_model=List[IndustryConfig])
async def get_industries():
    """获取行业配置列表"""
    config_path = Path("config.json")
    
    if not config_path.exists():
        return []
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            industries = config.get("industries", [])
            return [IndustryConfig(**ind) for ind in industries]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"加载配置失败: {str(e)}")


@router.post("/industries", response_model=IndustryConfig)
async def create_industry(industry: IndustryConfig):
    """添加新行业配置"""
    config_path = Path("config.json")
    
    try:
        # 读取现有配置
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        else:
            config = {"industries": [], "search_config": {}, "summary_config": {}}
        
        # 检查是否已存在
        for ind in config["industries"]:
            if ind["name"] == industry.name:
                raise HTTPException(status_code=400, detail="行业已存在")
        
        # 添加新行业
        config["industries"].append(industry.model_dump())
        
        # 保存
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return industry
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存配置失败: {str(e)}")


@router.put("/industries/{industry_name}", response_model=IndustryConfig)
async def update_industry(industry_name: str, industry: IndustryConfig):
    """更新行业配置"""
    config_path = Path("config.json")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 查找并更新
        found = False
        for i, ind in enumerate(config["industries"]):
            if ind["name"] == industry_name:
                config["industries"][i] = industry.model_dump()
                found = True
                break
        
        if not found:
            raise HTTPException(status_code=404, detail="行业不存在")
        
        # 保存
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return industry
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新配置失败: {str(e)}")


@router.delete("/industries/{industry_name}")
async def delete_industry(industry_name: str):
    """删除行业配置"""
    config_path = Path("config.json")
    
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)
        
        # 删除
        original_len = len(config["industries"])
        config["industries"] = [
            ind for ind in config["industries"]
            if ind["name"] != industry_name
        ]
        
        if len(config["industries"]) == original_len:
            raise HTTPException(status_code=404, detail="行业不存在")
        
        # 保存
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        
        return {"message": "删除成功"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除配置失败: {str(e)}")


# ==================== 任务管理接口 ====================

@router.post("/tasks/trigger")
async def trigger_task(background_tasks: BackgroundTasks):
    """手动触发情报采集任务"""
    background_tasks.add_task(trigger_manual_collection)
    return {
        "message": "任务已触发，正在后台执行",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/tasks/status")
async def get_task_status():
    """获取任务调度器状态"""
    status = get_scheduler_status()
    return status


# ==================== 飞书推送测试接口 ====================

@router.post("/notification/test")
async def test_notification_push():
    """测试飞书推送"""
    notification_service = get_notification_service()
    success = await notification_service.send_test_message()
    
    if success:
        return {"message": "测试消息发送成功"}
    else:
        raise HTTPException(status_code=500, detail="测试消息发送失败")


# ==================== 系统配置接口 ====================

@router.get("/config/ai-provider")
async def get_ai_provider():
    """获取当前AI提供商"""
    return {
        "provider": settings.ai_provider,
        "model": {
            "deepseek": settings.deepseek_model,
            "ollama": settings.ollama_model
        }.get(settings.ai_provider, "unknown")
    }


@router.get("/config/schedule")
async def get_schedule_config():
    """获取定时任务配置"""
    return {
        "times": settings.schedule_times_list,
        "timezone": settings.timezone
    }