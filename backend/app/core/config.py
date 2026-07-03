from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


class Settings(BaseSettings):
    """应用配置"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # AI模型配置
    ai_provider: str = "deepseek"
    
    # DeepSeek
    deepseek_api_key: Optional[str] = None
    deepseek_base_url: str = "https://api.deepseek.com"
    deepseek_model: str = "deepseek-chat"
    
    # Ollama（本地部署）
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:3b"
    
    # Web搜索API
    serper_api_key: Optional[str] = None
    google_search_api_key: Optional[str] = None
    google_search_engine_id: Optional[str] = None
    bing_search_api_key: Optional[str] = None
    
    # 飞书机器人
    feishu_webhook_url: Optional[str] = None
    
    # 存储配置
    excel_dir: str = "./data"
    database_url: str = "sqlite:///./data/intelligence.db"
    
    # 定时任务配置
    schedule_times: str = "09:00,18:00"
    timezone: str = "Asia/Shanghai"
    
    # 前端地址
    frontend_url: str = "http://localhost:3000"
    
    @property
    def schedule_times_list(self) -> List[str]:
        """解析定时任务时间列表"""
        return [t.strip() for t in self.schedule_times.split(",") if t.strip()]


# 全局配置实例
settings = Settings()