"""Feature flags management module."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class FeatureConfig(BaseModel):
    """Configuration for a feature."""
    
    name: str
    description: str
    enabled: bool = False
    version: str = "1.0.0"
    dependencies: List[str] = Field(default_factory=list)
    configuration: Dict[str, Any] = Field(default_factory=dict)


class FeatureFlags:
    """Manages feature flags for the system."""
    
    def __init__(self, features: Optional[Dict[str, FeatureConfig]] = None):
        """Initialize feature flags manager.
        
        Args:
            features: Dictionary of feature configurations.
        """
        self._features = features or {}
        self._enabled_features: set = set()
    
    def register_feature(self, feature: FeatureConfig) -> None:
        """Register a new feature.
        
        Args:
            feature: Feature configuration to register.
        """
        self._features[feature.name] = feature
    
    def enable_feature(self, feature_name: str) -> bool:
        """Enable a feature.
        
        Args:
            feature_name: Name of the feature to enable.
            
        Returns:
            True if feature was enabled, False if not found.
        """
        if feature_name in self._features:
            self._features[feature_name].enabled = True
            self._enabled_features.add(feature_name)
            return True
        return False
    
    def disable_feature(self, feature_name: str) -> bool:
        """Disable a feature.
        
        Args:
            feature_name: Name of the feature to disable.
            
        Returns:
            True if feature was disabled, False if not found.
        """
        if feature_name in self._features:
            self._features[feature_name].enabled = False
            self._enabled_features.discard(feature_name)
            return True
        return False
    
    def is_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled.
        
        Args:
            feature_name: Name of the feature to check.
            
        Returns:
            True if feature is enabled, False otherwise.
        """
        feature = self._features.get(feature_name)
        return feature is not None and feature.enabled
    
    def get_feature(self, feature_name: str) -> Optional[FeatureConfig]:
        """Get feature configuration.
        
        Args:
            feature_name: Name of the feature.
            
        Returns:
            Feature configuration or None if not found.
        """
        return self._features.get(feature_name)
    
    def get_feature_config(self, feature_name: str) -> Dict[str, Any]:
        """Get feature configuration as a dictionary.
        
        Args:
            feature_name: Name of the feature.
            
        Returns:
            Feature configuration dictionary.
        """
        feature = self.get_feature(feature_name)
        if feature:
            return {
                "name": feature.name,
                "description": feature.description,
                "enabled": feature.enabled,
                "version": feature.version,
                "configuration": feature.configuration,
            }
        return {}
    
    def get_enabled_features(self) -> List[str]:
        """Get list of enabled feature names.
        
        Returns:
            List of enabled feature names.
        """
        return list(self._enabled_features)
    
    def get_all_features(self) -> Dict[str, Dict[str, Any]]:
        """Get all features with their configurations.
        
        Returns:
            Dictionary of feature names to configurations.
        """
        return {
            name: {
                "name": feature.name,
                "description": feature.description,
                "enabled": feature.enabled,
                "version": feature.version,
                "dependencies": feature.dependencies,
                "configuration": feature.configuration,
            }
            for name, feature in self._features.items()
        }
    
    def check_dependencies(self, feature_name: str) -> tuple[bool, List[str]]:
        """Check if feature dependencies are met.
        
        Args:
            feature_name: Name of the feature to check.
            
        Returns:
            Tuple of (all_dependencies_met, list_of_missing_dependencies).
        """
        feature = self._features.get(feature_name)
        if not feature:
            return False, [feature_name]
        
        missing = []
        for dep in feature.dependencies:
            if not self.is_enabled(dep):
                missing.append(dep)
        
        return len(missing) == 0, missing
    
    def enable_feature_with_dependencies(
        self, feature_name: str, recursive: bool = True
    ) -> tuple[bool, List[str]]:
        """Enable a feature and its dependencies.
        
        Args:
            feature_name: Name of the feature to enable.
            recursive: Whether to recursively enable dependencies.
            
        Returns:
            Tuple of (success, list_of_failed_dependencies).
        """
        feature = self._features.get(feature_name)
        if not feature:
            return False, [feature_name]
        
        failed = []
        
        if recursive:
            for dep in feature.dependencies:
                success, failed_deps = self.enable_feature_with_dependencies(dep)
                if not success:
                    failed.extend(failed_deps)
        
        if not self.enable_feature(feature_name):
            failed.append(feature_name)
        
        return len(failed) == 0, failed


class FeatureManager:
    """High-level feature management interface."""
    
    def __init__(self, config_dir: Optional[str] = None):
        """Initialize the feature manager.
        
        Args:
            config_dir: Path to the configuration directory.
        """
        self._flags = FeatureFlags()
        self._load_default_features()
    
    def _load_default_features(self) -> None:
        """Load default feature configurations."""
        from .config_loader import get_config_loader
        
        try:
            loader = get_config_loader(config_dir)
            features_data = loader.load_features()
            
            for name, config in features_data.items():
                self._flags.register_feature(
                    FeatureConfig(
                        name=name,
                        description=config.get("description", ""),
                        enabled=config.get("enabled", False),
                        version=config.get("version", "1.0.0"),
                        dependencies=config.get("dependencies", []),
                        configuration=config.get("configuration", {}),
                    )
                )
        except Exception:
            pass
    
    def setup_features(self, enabled_features: Optional[List[str]] = None) -> None:
        """Set up feature flags with optional enabled features.
        
        Args:
            enabled_features: List of feature names to enable.
        """
        if enabled_features:
            for feature in enabled_features:
                self._flags.enable_feature(feature)
    
    def is_enabled(self, feature_name: str) -> bool:
        """Check if a feature is enabled."""
        return self._flags.is_enabled(feature_name)
    
    def get_config(self, feature_name: str) -> Dict[str, Any]:
        """Get feature configuration."""
        return self._flags.get_feature_config(feature_name)
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Get all features."""
        return self._flags.get_all_features()
    
    def get_enabled(self) -> List[str]:
        """Get enabled features."""
        return self._flags.get_enabled_features()


def get_feature_manager(config_dir: Optional[str] = None) -> FeatureManager:
    """Get feature manager instance.
    
    Args:
        config_dir: Path to the configuration directory.
        
    Returns:
        FeatureManager instance.
    """
    return FeatureManager(config_dir)
