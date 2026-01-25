"""JSON parsing utilities."""

import json
from typing import Any, Dict, List, Optional


class JSONParser:
    """JSON parsing utilities."""
    
    @staticmethod
    def parse(content: str) -> Any:
        """Parse JSON string.
        
        Args:
            content: JSON string.
            
        Returns:
            Parsed JSON.
        """
        return json.loads(content)
    
    @staticmethod
    def parse_safe(content: str, default: Any = None) -> Any:
        """Safely parse JSON with fallback.
        
        Args:
            content: JSON string.
            default: Default value on error.
            
        Returns:
            Parsed JSON or default.
        """
        try:
            return json.loads(content)
        except (json.JSONDecodeError, TypeError):
            return default
    
    @staticmethod
    def parse_dict(content: str) -> Dict[str, Any]:
        """Parse JSON as dictionary.
        
        Args:
            content: JSON string.
            
        Returns:
            Parsed dictionary.
        """
        return json.loads(content)
    
    @staticmethod
    def parse_list(content: str) -> List[Any]:
        """Parse JSON as list.
        
        Args:
            content: JSON string.
            
        Returns:
            Parsed list.
        """
        return json.loads(content)
    
    @staticmethod
    def stringify(obj: Any, indent: int = 2) -> str:
        """Stringify object to JSON.
        
        Args:
            obj: Object to stringify.
            indent: Indentation.
            
        Returns:
            JSON string.
        """
        return json.dumps(obj, indent=indent)
    
    @staticmethod
    def extract_field(content: str, field: str) -> Any:
        """Extract field from JSON.
        
        Args:
            content: JSON string.
            field: Field name.
            
        Returns:
            Field value or None.
        """
        try:
            data = json.loads(content)
            return data.get(field)
        except json.JSONDecodeError:
            return None
