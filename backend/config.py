"""
配置管理模块
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path


class Settings(BaseSettings):
    """应用配置"""
    
    # Basic Settings
    app_name: str = "labors_assistant"
    app_version: str = "0.1.0"
    debug: bool = True
    log_level: str = "INFO"
    
    # Server Settings
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    workers: int = 4
    
    # Database Settings
    database_url: str = "sqlite:///./storage/db/labors_assistant.db"
    
    # LLM Configuration
    LLM_api_key: str = ""
    LLM_model: str = "qwen3.5-plus"
    
    # Legal API Configuration (得理法律平台)
    legal_api_base_url: str = "https://openapi.delilegal.com/api/qa/v3/search"
    legal_api_appid: str = ""
    legal_api_secret: str = ""
    
    # Storage Settings
    document_storage_path: str = "./storage/documents/"
    template_storage_path: str = "./storage/templates/"
    
    # Security Settings
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Feature Flags
    enable_user_auth: bool = False
    enable_case_search: bool = True
    enable_law_search: bool = True
    enable_document_export: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def database_url_safe(self) -> str:
        """返回数据库连接URL，用于显示（隐藏密码）"""
        if "postgresql" in self.database_url:
            # postgresql://user:****@host/db
            return self.database_url.split("://")[0] + "://****:****@" + self.database_url.split("@")[1]
        return self.database_url


@lru_cache
def get_settings() -> Settings:
    """单例模式获取配置"""
    return Settings()
