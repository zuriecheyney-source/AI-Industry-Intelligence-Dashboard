from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import logging
import json
from pathlib import Path
from typing import Dict, List, Any
import uuid

from app.core.config import settings
from app.models.intelligence import Intelligence, IndustryConfig
from app.services.search_service import get_search_service
from app.services.ai_service import get_ai_service
from app.services.excel_service import get_excel_service
from app.services.notification_service import get_notification_service

logger = logging.getLogger(__name__)


class IntelligenceTask:
    """情报采集任务"""
    
    def __init__(self):
        self.task_id = None
        self.is_running = False
        self.search_service = get_search_service()
        self.ai_service = get_ai_service()
        self.excel_service = get_excel_service()
        self.notification_service = get_notification_service()
    
    def _load_industry_configs(self) -> List[Dict[str, Any]]:
        """加载行业配置"""
        config_path = Path("config.json")
        
        if not config_path.exists():
            logger.warning("配置文件不存在，使用默认配置")
            return []
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
                return config.get("industries", [])
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            return []
    
    async def execute_daily_collection(self) -> Dict[str, Any]:
        """执行每日情报采集任务"""
        
        if self.is_running:
            logger.warning("任务已在运行中，跳过本次执行")
            return {"status": "skipped", "message": "任务已在运行中"}
        
        self.is_running = True
        self.task_id = str(uuid.uuid4())
        start_time = datetime.now()
        
        logger.info(f"开始执行每日情报采集任务 - ID: {self.task_id}")
        
        try:
            # 1. 加载行业配置
            industry_configs = self._load_industry_configs()
            if not industry_configs:
                raise ValueError("没有配置任何行业")
            
            logger.info(f"加载配置: {len(industry_configs)} 个行业")
            
            # 2. 搜索情报
            search_results = await self.search_service.search_multiple_industries(
                industry_configs=industry_configs,
                max_results_per_keyword=5,
                date_range_days=1
            )
            
            total_search_results = sum(len(results) for results in search_results.values())
            logger.info(f"搜索完成: 共 {total_search_results} 条原始结果")
            
            if total_search_results == 0:
                logger.warning("未搜索到任何结果")
                return {
                    "status": "completed",
                    "message": "未搜索到任何结果",
                    "intelligence_count": 0
                }
            
            # 3. AI分析情报
            all_intelligence: Dict[str, List[Intelligence]] = {}
            
            for industry, results in search_results.items():
                if not results:
                    continue
                
                analyzed = await self.ai_service.batch_analyze(results)
                
                # 转换为 Intelligence 对象
                intelligence_list = []
                for item in analyzed:
                    try:
                        intel = Intelligence(
                            industry=item["industry"],
                            title=item["title"],
                            summary=item["summary"],
                            source_url=item["url"],
                            source_name=item.get("source", ""),
                            category=item["category"],
                            importance=item["importance"],
                            keywords=item["keywords"]
                        )
                        intelligence_list.append(intel)
                    except Exception as e:
                        logger.error(f"转换Intelligence对象失败: {str(e)}")
                        continue
                
                all_intelligence[industry] = intelligence_list
            
            total_intelligence = sum(len(items) for items in all_intelligence.values())
            logger.info(f"AI分析完成: 共 {total_intelligence} 条情报")
            
            # 4. 保存到Excel
            all_items = []
            for items in all_intelligence.values():
                all_items.extend(items)
            
            save_stats = self.excel_service.batch_save_intelligence(all_items)
            logger.info(f"Excel保存完成: {save_stats}")
            
            # 5. 推送到飞书
            if total_intelligence > 0:
                push_success = await self.notification_service.send_daily_intelligence(
                    intelligence_by_industry=all_intelligence
                )
                logger.info(f"飞书推送: {'成功' if push_success else '失败'}")
            
            # 6. 即时推送高重要度情报
            for items in all_intelligence.values():
                for intel in items:
                    if intel.importance == "高":
                        await self.notification_service.send_urgent_intelligence(intel)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            result = {
                "status": "completed",
                "task_id": self.task_id,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration,
                "intelligence_count": total_intelligence,
                "save_stats": save_stats,
                "industries": list(all_intelligence.keys())
            }
            
            logger.info(f"任务执行完成 - 耗时 {duration:.2f}秒, 共 {total_intelligence} 条情报")
            return result
            
        except Exception as e:
            logger.error(f"任务执行失败: {str(e)}", exc_info=True)
            return {
                "status": "failed",
                "task_id": self.task_id,
                "error": str(e)
            }
        
        finally:
            self.is_running = False


# 全局任务调度器
_scheduler: AsyncIOScheduler = None
_intelligence_task: IntelligenceTask = None


def init_scheduler() -> AsyncIOScheduler:
    """初始化定时任务调度器"""
    global _scheduler, _intelligence_task
    
    if _scheduler is not None:
        return _scheduler
    
    _scheduler = AsyncIOScheduler(timezone=settings.timezone)
    _intelligence_task = IntelligenceTask()
    
    # 添加定时任务
    for schedule_time in settings.schedule_times_list:
        hour, minute = schedule_time.split(":")
        
        _scheduler.add_job(
            _intelligence_task.execute_daily_collection,
            trigger=CronTrigger(hour=int(hour), minute=int(minute)),
            id=f"daily_collection_{schedule_time}",
            name=f"每日情报采集 {schedule_time}",
            replace_existing=True
        )
        
        logger.info(f"添加定时任务: 每日 {schedule_time} 执行情报采集")
    
    return _scheduler


def start_scheduler():
    """启动调度器"""
    global _scheduler
    
    if _scheduler is None:
        init_scheduler()
    
    if not _scheduler.running:
        _scheduler.start()
        logger.info("定时任务调度器已启动")


def stop_scheduler():
    """停止调度器"""
    global _scheduler
    
    if _scheduler and _scheduler.running:
        _scheduler.shutdown()
        logger.info("定时任务调度器已停止")


async def trigger_manual_collection() -> Dict[str, Any]:
    """手动触发情报采集"""
    global _intelligence_task
    
    if _intelligence_task is None:
        _intelligence_task = IntelligenceTask()
    
    logger.info("手动触发情报采集任务")
    return await _intelligence_task.execute_daily_collection()


def get_scheduler_status() -> Dict[str, Any]:
    """获取调度器状态"""
    global _scheduler
    
    if _scheduler is None:
        return {"running": False, "jobs": []}
    
    jobs = []
    for job in _scheduler.get_jobs():
        jobs.append({
            "id": job.id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
        })
    
    return {
        "running": _scheduler.running,
        "timezone": str(_scheduler.timezone),
        "jobs": jobs
    }