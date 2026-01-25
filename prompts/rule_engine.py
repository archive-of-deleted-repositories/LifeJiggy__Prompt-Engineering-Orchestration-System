"""Rule engine for prompt constraints and validation."""


class RuleEngine:
    """Evaluates and enforces prompt rules and constraints."""
    
    def __init__(self, rules_dir: str = "./prompts/rules"):
        """Initialize the rule engine.
        
        Args:
            rules_dir: Directory containing rule definitions.
        """
        self.rules_dir = rules_dir
        self._rules = {
            "hard": [],
            "soft": [],
            "conditional": [],
        }
    
    def add_hard_rule(self, rule: dict) -> bool:
        """Add a hard (non-negotiable) rule.
        
        Args:
            rule: Rule configuration.
            
        Returns:
            True if successful.
        """
        self._rules["hard"].append(rule)
        return True
    
    def add_soft_rule(self, rule: dict) -> bool:
        """Add a soft (preference) rule.
        
        Args:
            rule: Rule configuration.
            
        Returns:
            True if successful.
        """
        self._rules["soft"].append(rule)
        return True
    
    def add_conditional_rule(self, rule: dict) -> bool:
        """Add a conditional rule.
        
        Args:
            rule: Rule configuration with condition.
            
        Returns:
            True if successful.
        """
        self._rules["conditional"].append(rule)
        return True
    
    def validate_prompt(self, prompt: str, context: dict) -> tuple[bool, list[str]]:
        """Validate a prompt against all rules.
        
        Args:
            prompt: Prompt string to validate.
            context: Context for conditional rules.
            
        Returns:
            Tuple of (is_valid, list_of_violations).
        """
        violations = []
        
        for rule in self._rules["hard"]:
            if not self._check_rule(prompt, rule):
                violations.append(rule.get("message", "Hard rule violation"))
        
        return len(violations) == 0, violations
    
    def _check_rule(self, prompt: str, rule: dict) -> bool:
        """Check a single rule against a prompt.
        
        Args:
            prompt: Prompt string.
            rule: Rule configuration.
            
        Returns:
            True if rule passes, False otherwise.
        """
        pattern = rule.get("pattern", "")
        if pattern and pattern in prompt:
            return False
        return True
    
    def get_rules_summary(self) -> dict:
        """Get summary of all rules.
        
        Returns:
            Dictionary with rule counts by type.
        """
        return {
            "hard_rules": len(self._rules["hard"]),
            "soft_rules": len(self._rules["soft"]),
            "conditional_rules": len(self._rules["conditional"]),
        }
