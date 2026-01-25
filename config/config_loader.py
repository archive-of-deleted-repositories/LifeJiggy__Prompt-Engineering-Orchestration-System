"""Configuration loader for YAML-based configuration files."""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache
import yaml
from pydantic import BaseModel, Field


class ModelConfig(BaseModel):
    """Configuration for an AI model."""
    
    name: str
    provider: str
    max_tokens: int = 4096
    temperature: float = 0.7
    streaming: bool = True
    timeout: int = 120
    retry_attempts: int = 3
    fallback: Optional[str] = None
    capabilities: list[str] = Field(default_factory=list)
    input_cost_per_1k_tokens: Optional[float] = None
    output_cost_per_1k_tokens: Optional[float] = None


class EmbeddingConfig(BaseModel):
    """Configuration for an embedding model."""
    
    name: str
    provider: str
    dimensions: int = 1536
    max_tokens: int = 8191
    capabilities: list[str] = Field(default_factory=list)


class EnvironmentConfig(BaseModel):
    """Configuration for a specific environment."""
    
    name: str
    description: str
    debug_mode: bool = False
    log_level: str = "INFO"
    api_keys: Dict[str, str] = Field(default_factory=dict)
    vector_database: Dict[str, Any] = Field(default_factory=dict)
    mcp_servers: Dict[str, Any] = Field(default_factory=dict)
    model_defaults: Dict[str, Any] = Field(default_factory=dict)
    rate_limits: Dict[str, int] = Field(default_factory=dict)
    cache: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    cors: Dict[str, Any] = Field(default_factory=dict)
    security: Dict[str, Any] = Field(default_factory=dict)


class FeatureConfig(BaseModel):
    """Configuration for a feature flag."""
    
    name: str
    description: str
    enabled: bool = False
    version: str = "1.0.0"
    dependencies: list[str] = Field(default_factory=list)
    configuration: Dict[str, Any] = Field(default_factory=dict)


class ConfigLoader:
    """Loader for YAML configuration files."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the config loader.
        
        Args:
            config_dir: Path to the configuration directory. Defaults to ./config.
        """
        if config_dir is None:
            config_dir = os.environ.get(
                "CONFIG_DIR",
                str(Path(__file__).parent.parent / "config")
            )
        self.config_dir = Path(config_dir)
    
    def load_yaml(self, filename: str) -> Dict[str, Any]:
        """Load a YAML configuration file.
        
        Args:
            filename: Name of the YAML file to load.
            
        Returns:
            Parsed YAML configuration as a dictionary.
        """
        filepath = self.config_dir / filename
        if not filepath.exists():
            raise FileNotFoundError(f"Configuration file not found: {filepath}")
        
        with open(filepath, "r") as f:
            return yaml.safe_load(f)
    
    def load_models(self) -> Dict[str, ModelConfig]:
        """Load model configurations from models.yaml.
        
        Returns:
            Dictionary of model configurations.
        """
        config = self.load_yaml("models.yaml")
        models = {}
        
        for model_name, model_data in config.get("models", {}).items():
            models[model_name] = ModelConfig(
                name=model_name,
                **model_data,
                input_cost_per_1k_tokens=model_data.get("input_cost_per_1k_tokens"),
                output_cost_per_1k_tokens=model_data.get("output_cost_per_1k_tokens"),
            )
        
        for emb_name, emb_data in config.get("embedding_models", {}).items():
            models[emb_name] = ModelConfig(
                name=emb_name,
                provider=emb_data.get("provider", "openai"),
                max_tokens=emb_data.get("max_tokens", 8191),
                capabilities=emb_data.get("capabilities", []),
            )
        
        return models
    
    def load_environments(self) -> Dict[str, EnvironmentConfig]:
        """Load environment configurations from environments.yaml.
        
        Returns:
            Dictionary of environment configurations.
        """
        config = self.load_yaml("environments.yaml")
        environments = {}
        
        for env_name, env_data in config.get("environments", {}).items():
            environments[env_name] = EnvironmentConfig(
                name=env_name,
                **env_data,
            )
        
        return environments
    
    def load_features(self) -> Dict[str, FeatureConfig]:
        """Load feature flag configurations from feature_flags.yaml.
        
        Returns:
            Dictionary of feature configurations.
        """
        config = self.load_yaml("feature_flags.yaml")
        features = {}
        
        for feat_name, feat_data in config.get("features", {}).items():
            features[feat_name] = FeatureConfig(
                name=feat_name,
                **feat_data,
            )
        
        return features
    
    def load_all(self) -> Dict[str, Any]:
        """Load all configuration files.
        
        Returns:
            Dictionary containing all configurations.
        """
        return {
            "models": self.load_models(),
            "environments": self.load_environments(),
            "features": self.load_features(),
        }


@lru_cache()
def get_config_loader(config_dir: Optional[str] = None) -> ConfigLoader:
    """Get cached config loader instance.
    
    Args:
        config_dir: Path to the configuration directory.
        
    Returns:
        ConfigLoader instance.
    """
    return ConfigLoader(config_dir)


def load_config(config_type: str, config_dir: Optional[str] = None) -> Dict[str, Any]:
    """Load a specific configuration type.
    
    Args:
        config_type: Type of configuration to load (models, environments, features).
        config_dir: Path to the configuration directory.
        
    Returns:
        Configuration dictionary.
    """
    loader = get_config_loader(config_dir)
    
    if config_type == "models":
        return loader.load_models()
    elif config_type == "environments":
        return loader.load_environments()
    elif config_type == "features":
        return loader.load_features()
    else:
        raise ValueError(f"Unknown config type: {config_type}")
