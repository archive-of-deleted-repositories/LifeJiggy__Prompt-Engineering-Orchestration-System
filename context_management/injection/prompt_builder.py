"""Prompt builder for context injection."""

from typing import List, Dict, Any, Optional
from utilities.token_counter import TokenCounter


class PromptBuilder:
    """Builds prompts by injecting context."""
    
    def __init__(self, token_counter: TokenCounter = None):
        """Initialize the prompt builder.
        
        Args:
            token_counter: TokenCounter instance.
        """
        self.token_counter = token_counter or TokenCounter()
        self._system_template = ""
        self._context_formatters = {}
    
    def set_system_template(self, template: str) -> None:
        """Set the system prompt template.
        
        Args:
            template: System prompt template.
        """
        self._system_template = template
    
    def register_context_formatter(self, context_type: str, formatter) -> None:
        """Register a context formatter.
        
        Args:
            context_type: Type of context.
            formatter: Formatter function.
        """
        self._context_formatters[context_type] = formatter
    
    def build_system_prompt(
        self,
        base_template: str = None,
        context: Dict[str, Any] = None,
        max_tokens: int = 4000
    ) -> str:
        """Build system prompt with context.
        
        Args:
            base_template: Base template.
            context: Context to inject.
            max_tokens: Maximum tokens.
            
        Returns:
            Built system prompt.
        """
        template = base_template or self._system_template
        
        if not context:
            return template
        
        context_parts = []
        
        for ctx_type, ctx_data in context.items():
            if ctx_type in self._context_formatters:
                formatted = self._context_formatters[ctx_type](ctx_data)
                context_parts.append(formatted)
            elif isinstance(ctx_data, list):
                for item in ctx_data:
                    context_parts.append(str(item))
            else:
                context_parts.append(str(ctx_data))
        
        context_text = "\n\n".join(context_parts)
        
        if "{context}" in template:
            prompt = template.replace("{context}", context_text)
        else:
            prompt = f"{template}\n\n## Additional Context\n\n{context_text}"
        
        while self.token_counter.count_tokens(prompt) > max_tokens and context_parts:
            context_parts.pop()
            context_text = "\n\n".join(context_parts)
            if "{context}" in template:
                prompt = template.replace("{context}", context_text)
            else:
                prompt = f"{template}\n\n## Additional Context\n\n{context_text}"
        
        return prompt
    
    def build_messages(
        self,
        system_prompt: str,
        conversation: List[Dict[str, str]],
        context: Dict[str, Any] = None,
        max_total_tokens: int = 8000
    ) -> List[Dict[str, str]]:
        """Build message list with context.
        
        Args:
            system_prompt: System prompt.
            conversation: Conversation history.
            context: Additional context.
            max_total_tokens: Maximum total tokens.
            
        Returns:
            List of messages.
        """
        augmented_system = self.build_system_prompt(
            base_template=system_prompt,
            context=context
        )
        
        messages = [{"role": "system", "content": augmented_system}]
        
        for msg in conversation:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        return messages
    
    def extract_context_placeholders(self, template: str) -> List[str]:
        """Extract context placeholders from template.
        
        Args:
            template: Template string.
            
        Returns:
            List of placeholder names.
        """
        import re
        placeholders = re.findall(r"\{(\w+)\}", template)
        return list(set(placeholders))
