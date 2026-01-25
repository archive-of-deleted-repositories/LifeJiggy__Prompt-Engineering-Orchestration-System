"""Regression tests to prevent breaking changes."""

import pytest


class TestPromptRegression:
    """Regression tests for prompt functionality."""
    
    def test_prompt_template_backwards_compatibility(self):
        """Ensure old prompt templates still work."""
        from prompts.template_engine import TemplateEngine
        
        engine = TemplateEngine()
        
        template = "Hello {name}, welcome to {platform}!"
        result = engine.render(template, {"name": "User", "platform": "our system"})
        
        assert "Hello User" in result
        assert "welcome to our system" in result
    
    def test_skill_library_compatibility(self):
        """Ensure skills can still be retrieved by ID."""
        from prompts.skill_library import SkillLibrary
        
        library = SkillLibrary()
        library.register_skill("coding", {"category": "development"})
        
        skill = library.get_skill("coding")
        assert skill is not None
        assert skill.get("category") == "development"


class TestRuleEngineRegression:
    """Regression tests for rule engine."""
    
    def test_hard_rules_always_enforced(self):
        """Ensure hard rules are always checked."""
        from prompts.rule_engine import RuleEngine
        
        engine = RuleEngine()
        engine.add_hard_rule({
            "pattern": "illegal",
            "message": "Illegal content not allowed"
        })
        
        is_valid, _ = engine.validate_prompt("This is illegal content", {})
        assert is_valid is False
    
    def test_rule_summary_works(self):
        """Ensure rule summary returns correct counts."""
        from prompts.rule_engine import RuleEngine
        
        engine = RuleEngine()
        engine.add_hard_rule({"pattern": "test1"})
        engine.add_soft_rule({"pattern": "test2"})
        
        summary = engine.get_rules_summary()
        
        assert summary["hard_rules"] == 1
        assert summary["soft_rules"] == 1


class TestMemoryRegression:
    """Regression tests for memory systems."""
    
    def test_short_term_memory_order_preserved(self):
        """Ensure message order is preserved."""
        from context_management.memory import ShortTermMemory
        
        memory = ShortTermMemory(max_messages=10)
        messages = [
            {"role": "user", "content": "First"},
            {"role": "assistant", "content": "Second"},
            {"role": "user", "content": "Third"}
        ]
        
        for msg in messages:
            memory.add(msg)
        
        retrieved = memory.get_all()
        assert len(retrieved) == 3
        assert retrieved[0]["content"] == "First"
    
    def test_long_term_memory_persistence(self):
        """Ensure long-term memory can store and retrieve facts."""
        from context_management.memory import LongTermMemory
        
        memory = LongTermMemory()
        memory.add_fact("user123", "Prefers Python")
        
        facts = memory.get_facts("user123")
        assert len(facts) == 1
        assert facts[0]["fact"] == "Prefers Python"


class TestAPIReggression:
    """Regression tests for API endpoints."""
    
    def test_health_endpoint_structure(self):
        """Ensure health endpoint returns expected structure."""
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "version" in data


class TestConfigurationRegression:
    """Regression tests for configuration."""
    
    def test_settings_load(self):
        """Ensure settings can be loaded."""
        from config.settings import get_settings
        
        settings = get_settings()
        assert settings is not None
        assert hasattr(settings, "environment")
    
    def test_feature_flags_work(self):
        """Ensure feature flags can be queried."""
        from config.feature_flags import get_feature_manager
        
        manager = get_feature_manager()
        features = manager.get_all()
        
        assert isinstance(features, dict)
