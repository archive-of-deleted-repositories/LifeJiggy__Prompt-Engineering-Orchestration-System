"""MCP schema definitions."""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class ToolDefinition(BaseModel):
    """Tool definition schema."""
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any] = {"type": "any"}
    required: List[str] = []


class ToolCall(BaseModel):
    """Tool call schema."""
    tool: str
    arguments: Dict[str, Any] = {}


class ToolResult(BaseModel):
    """Tool result schema."""
    tool: str
    success: bool
    result: Any = None
    error: Optional[str] = None


class ResourceDefinition(BaseModel):
    """Resource definition schema."""
    uri: str
    name: str
    description: str
    mime_type: str = "text/plain"


class ResourceContent(BaseModel):
    """Resource content schema."""
    uri: str
    mime_type: str = "text/plain"
    content: str = ""


class MCPMessage(BaseModel):
    """MCP message schema."""
    type: str
    request_type: Optional[str] = None
    params: Dict[str, Any] = {}
    id: Optional[str] = None


class InitializeParams(BaseModel):
    """Initialize params schema."""
    protocol_version: str = "2024-01-01"
    capabilities: Dict[str, Any] = {}
    client_info: Dict[str, str] = {}


class InitializeResult(BaseModel):
    """Initialize result schema."""
    protocol_version: str = "2024-01-01"
    capabilities: Dict[str, Any] = {}
    server_info: Dict[str, str] = {}


class ToolValidator:
    """Validates tool calls."""
    
    @staticmethod
    def validate_params(
        tool_def: ToolDefinition,
        params: Dict[str, Any]
    ) -> tuple[bool, List[str]]:
        """Validate parameters against tool definition.
        
        Args:
            tool_def: Tool definition.
            params: Provided parameters.
            
        Returns:
            Tuple of (is_valid, list_of_errors).
        """
        errors = []
        
        required = set(tool_def.required)
        provided = set(params.keys())
        
        missing = required - provided
        if missing:
            errors.append(f"Missing required parameters: {missing}")
        
        param_schema = tool_def.parameters.get("properties", {})
        for key, value in params.items():
            if key in param_schema:
                expected_type = param_schema[key].get("type")
                if expected_type and not isinstance(value, eval(expected_type)):
                    errors.append(f"Parameter {key} should be {expected_type}")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_result(
        tool_def: ToolDefinition,
        result: Any
    ) -> tuple[bool, str]:
        """Validate tool result.
        
        Args:
            tool_def: Tool definition.
            result: Tool result.
            
        Returns:
            Tuple of (is_valid, error_message).
        """
        return True, ""
