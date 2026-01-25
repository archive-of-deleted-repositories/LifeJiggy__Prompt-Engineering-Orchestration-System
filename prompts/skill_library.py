"""Skill library for managing AI capabilities."""


class SkillLibrary:
    """Manages AI skills and their configurations."""
    
    def __init__(self, skills_dir: str = "./prompts/skills"):
        """Initialize the skill library.
        
        Args:
            skills_dir: Directory containing skill definitions.
        """
        self.skills_dir = skills_dir
        self._skills = {}
    
    def get_skill(self, skill_id: str) -> dict:
        """Get a skill by ID.
        
        Args:
            skill_id: Unique identifier for the skill.
            
        Returns:
            Skill configuration dictionary.
        """
        return self._skills.get(skill_id, {})
    
    def register_skill(self, skill_id: str, skill_config: dict) -> bool:
        """Register a new skill.
        
        Args:
            skill_id: Unique identifier for the skill.
            skill_config: Skill configuration.
            
        Returns:
            True if successful.
        """
        self._skills[skill_id] = skill_config
        return True
    
    def list_skills(self) -> list[str]:
        """List all registered skills.
        
        Returns:
            List of skill IDs.
        """
        return list(self._skills.keys())
    
    def get_skills_by_category(self, category: str) -> list[dict]:
        """Get skills by category.
        
        Args:
            category: Skill category to filter by.
            
        Returns:
            List of skill configurations.
        """
        return [
            {"id": k, **v}
            for k, v in self._skills.items()
            if v.get("category") == category
        ]
