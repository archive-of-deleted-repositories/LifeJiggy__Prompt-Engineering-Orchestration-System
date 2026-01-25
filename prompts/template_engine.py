"""Template engine for prompt rendering."""


class TemplateEngine:
    """Renders prompt templates with variable substitution."""
    
    def __init__(self, template_dir: str = "./prompts/templates"):
        """Initialize the template engine.
        
        Args:
            template_dir: Directory containing templates.
        """
        self.template_dir = template_dir
        self._templates = {}
    
    def render(self, template: str, context: dict) -> str:
        """Render a template with context.
        
        Args:
            template: Template string to render.
            context: Variables to substitute.
            
        Returns:
            Rendered template string.
        """
        result = template
        for key, value in context.items():
            placeholder = f"{{{{ {key} }}}}"
            result = result.replace(placeholder, str(value))
        return result
    
    def load_template(self, template_id: str) -> str:
        """Load a template by ID.
        
        Args:
            template_id: Unique identifier for the template.
            
        Returns:
            Template string.
        """
        return self._templates.get(template_id, "")
    
    def save_template(self, template_id: str, template: str) -> bool:
        """Save a template.
        
        Args:
            template_id: Unique identifier for the template.
            template: Template string to save.
            
        Returns:
            True if successful.
        """
        self._templates[template_id] = template
        return True
