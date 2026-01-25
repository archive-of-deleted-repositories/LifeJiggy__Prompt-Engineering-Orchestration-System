"""Settings management using Pydantic Settings."""

import os
from pathlib import Path
from functools import lru_cache
from typing import Optional, Dict, Any, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class APISettings(BaseSettings):
    """API configuration settings."""
    
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, alias="ANTHROPIC_API_KEY")
    google_api_key: Optional[str] = Field(default=None, alias="GOOGLE_API_KEY")
    
    model_config = SettingsConfigDict(env_prefix="", populate_by_name=True)


class VectorDatabaseSettings(BaseSettings):
    """Vector database configuration settings."""
    
    type: str = Field(default="chroma", alias="VECTOR_DB_TYPE")
    host: str = Field(default="localhost", alias="VECTOR_DB_HOST")
    port: int = Field(default=8000, alias="VECTOR_DB_PORT")
    url: Optional[str] = Field(default=None, alias="VECTOR_DB_URL")
    api_key: Optional[str] = Field(default=None, alias="VECTOR_DB_API_KEY")
    persistence_path: str = Field(default="./data/vector_db")
    
    model_config = SettingsConfigDict(populate_by_name=True)


class MCPSettings(BaseSettings):
    """MCP server configuration settings."""
    
    filesystem_enabled: bool = Field(default=True, alias="MCP_FILESYSTEM_ENABLED")
    filesystem_root: str = Field(default="./data", alias="MCP_FILESYSTEM_ROOT")
    database_enabled: bool = Field(default=False, alias="MCP_DATABASE_ENABLED")
    database_connection: Optional[str] = Field(default=None, alias="MCP_DATABASE_CONNECTION")
    github_enabled: bool = Field(default=False, alias="MCP_GITHUB_ENABLED")
    github_token: Optional[str] = Field(default=None, alias="MCP_GITHUB_TOKEN")
    slack_enabled: bool = Field(default=False, alias="MCP_SLACK_ENABLED")
    slack_token: Optional[str] = Field(default=None, alias="MCP_SLACK_TOKEN")
    google_drive_enabled: bool = Field(default=False, alias="MCP_GOOGLE_DRIVE_ENABLED")
    google_drive_credentials: Optional[str] = Field(default=None, alias="MCP_GOOGLE_DRIVE_CREDENTIALS")
    
    model_config = SettingsConfigDict(populate_by_name=True)


class RateLimitSettings(BaseSettings):
    """Rate limiting configuration settings."""
    
    requests_per_minute: int = Field(default=60, alias="RATE_LIMIT_REQUESTS_PER_MINUTE")
    tokens_per_minute: int = Field(default=100000, alias="RATE_LIMIT_TOKENS_PER_MINUTE")
    
    model_config = SettingsConfigDict(populate_by_name=True)


class CacheSettings(BaseSettings):
    """Cache configuration settings."""
    
    enabled: bool = Field(default=True)
    ttl: int = Field(default=3600)
    max_size: int = Field(default=1000)
    redis_host: Optional[str] = Field(default=None, alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_password: Optional[str] = Field(default=None, alias="REDIS_PASSWORD")
    
    model_config = SettingsConfigDict(populate_by_name=True)


class SecuritySettings(BaseSettings):
    """Security configuration settings."""
    
    jwt_secret_key: str = Field(default="change-me-in-production", alias="JWT_SECRET_KEY")
    encryption_key: str = Field(default="change-me-in-production", alias="ENCRYPTION_KEY")
    jwt_algorithm: str = Field(default="HS256")
    token_expire_minutes: int = Field(default=60)
    
    model_config = SettingsConfigDict(populate_by_name=True)


class CostSettings(BaseSettings):
    """Cost tracking and budget settings."""
    
    monthly_budget_usd: float = Field(default=100.0, alias="MONTHLY_BUDGET_USD")
    alert_threshold: float = Field(default=0.8, alias="COST_ALERT_THRESHOLD")
    cost_tracking_enabled: bool = Field(default=True)
    
    model_config = SettingsConfigDict(populate_by_name=True)


class MonitoringSettings(BaseSettings):
    """Monitoring and metrics configuration settings."""
    
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    metrics_enabled: bool = Field(default=True)
    prometheus_multiproc_dir: Optional[str] = Field(default=None, alias="PROMETHEUS_MULTIPROC_DIR")
    otel_exporter_endpoint: Optional[str] = Field(default=None, alias="OTEL_EXPORTER_OTLP_ENDPOINT")
    
    model_config = SettingsConfigDict(populate_by_name=True)


class CORSSettings(BaseSettings):
    """CORS configuration settings."""
    
    enabled: bool = Field(default=True)
    allow_origins: List[str] = Field(default_factory=lambda: ["http://localhost:3000", "http://localhost:8000"])
    allow_methods: List[str] = Field(default_factory=lambda: ["*"])
    allow_headers: List[str] = Field(default_factory=lambda: ["*"])
    
    model_config = SettingsConfigDict(populate_by_name=True)


class Settings(BaseSettings):
    """Main settings class for the prompt engineering system."""
    
    environment: str = Field(default="development", alias="ENVIRONMENT")
    debug: bool = Field(default=False, alias="DEBUG")
    
    api: APISettings = Field(default_factory=APISettings)
    vector_database: VectorDatabaseSettings = Field(default_factory=VectorDatabaseSettings)
    mcp: MCPSettings = Field(default_factory=MCPSettings)
    rate_limits: RateLimitSettings = Field(default_factory=RateLimitSettings)
    cache: CacheSettings = Field(default_factory=CacheSettings)
    security: SecuritySettings = Field(default_factory=SecuritySettings)
    cost: CostSettings = Field(default_factory=CostSettings)
    monitoring: MonitoringSettings = Field(default_factory=MonitoringSettings)
    cors: CORSSettings = Field(default_factory=CORSSettings)
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_by_name=True,
    )
    
    @field_validator("environment")
    @classmethod
    def validate_environment(cls, v: str) -> str:
        """Validate environment value."""
        valid_environments = ["development", "staging", "production"]
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


def reload_settings() -> Settings:
    """Reload settings from environment variables."""
    get_settings.cache_clear()
    return get_settings()
