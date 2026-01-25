"""Unit tests for prompt engineering system."""

import pytest


class TestPromptManager:
    """Tests for PromptManager."""
    
    def test_load_prompt(self):
        """Test loading a prompt."""
        from prompts.prompt_manager import PromptManager
        
        manager = PromptManager()
        manager.save_prompt("test", {"template": "Hello {name}"})
        
        prompt = manager.load_prompt("test")
        assert prompt["template"] == "Hello {name}"
    
    def test_list_prompts(self):
        """Test listing prompts."""
        from prompts.prompt_manager import PromptManager
        
        manager = PromptManager()
        manager.save_prompt("prompt1", {})
        manager.save_prompt("prompt2", {})
        
        prompts = manager.list_prompts()
        assert len(prompts) == 2
        assert "prompt1" in prompts


class TestTemplateEngine:
    """Tests for TemplateEngine."""
    
    def test_render_simple_template(self):
        """Test rendering a simple template."""
        from prompts.template_engine import TemplateEngine
        
        engine = TemplateEngine()
        result = engine.render(
            "Hello {name}!",
            {"name": "World"}
        )
        assert result == "Hello World!"
    
    def test_render_multiple_variables(self):
        """Test rendering with multiple variables."""
        from prompts.template_engine import TemplateEngine
        
        engine = TemplateEngine()
        result = engine.render(
            "{greeting}, {name}! You have {count} messages.",
            {"greeting": "Hello", "name": "Alice", "count": 5}
        )
        assert result == "Hello, Alice! You have 5 messages."


class TestRuleEngine:
    """Tests for RuleEngine."""
    
    def test_validate_prompt_pass(self):
        """Test prompt validation that passes."""
        from prompts.rule_engine import RuleEngine
        
        engine = RuleEngine()
        is_valid, violations = engine.validate_prompt(
            "Write a function to calculate fibonacci.",
            {}
        )
        assert is_valid is True
        assert len(violations) == 0
    
    def test_hard_rule_violation(self):
        """Test hard rule violation detection."""
        from prompts.rule_engine import RuleEngine
        
        engine = RuleEngine()
        engine.add_hard_rule({
            "pattern": "password",
            "message": "Password mention not allowed"
        })
        
        is_valid, violations = engine.validate_prompt(
            "Show me the password",
            {}
        )
        assert is_valid is False
        assert "Password mention not allowed" in violations


class TestSkillLibrary:
    """Tests for SkillLibrary."""
    
    def test_register_skill(self):
        """Test registering a skill."""
        from prompts.skill_library import SkillLibrary
        
        library = SkillLibrary()
        library.register_skill("coding", {
            "category": "development",
            "capabilities": ["code_generation"]
        })
        
        skill = library.get_skill("coding")
        assert skill["category"] == "development"
    
    def test_list_skills(self):
        """Test listing skills."""
        from prompts.skill_library import SkillLibrary
        
        library = SkillLibrary()
        library.register_skill("coding", {"category": "dev"})
        library.register_skill("writing", {"category": "creative"})
        
        skills = library.list_skills()
        assert len(skills) == 2


class TestTokenCounter:
    """Tests for TokenCounter."""
    
    def test_count_tokens(self):
        """Test token counting."""
        from utilities.token_counter import TokenCounter
        
        counter = TokenCounter("gpt-4")
        count = counter.count("Hello world")
        assert count > 0


class TestContextManager:
    """Tests for ContextManager."""
    
    def test_short_term_memory(self):
        """Test short-term memory operations."""
        from context_management.memory import ShortTermMemory
        
        memory = ShortTermMemory(max_messages=3)
        memory.add({"role": "user", "content": "Hello"})
        memory.add({"role": "assistant", "content": "Hi"})
        
        assert memory.get_count() == 2
        
        memory.add({"role": "user", "content": "Third"})
        memory.add({"role": "user", "content": "Fourth"})
        
        assert memory.get_count() == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
