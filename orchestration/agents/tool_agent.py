"""Advanced tool-using agent with full MCP integration."""

from typing import Dict, Any, List, Optional, Tuple
import asyncio
import logging
import time
from enum import Enum

from orchestration.agent import BaseAgent
from mcp.mcp_client import MCPClient
from utilities.llm_client import LLMClient, LLMResponse

logger = logging.getLogger(__name__)


class ToolExecutionStrategy(Enum):
    """Tool execution strategies."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    CONDITIONAL = "conditional"


class ToolCall:
    """Represents a tool execution."""
    
    def __init__(self, tool_name: str, parameters: Dict[str, Any], 
                 reasoning: str = "", call_id: str = None):
        """Initialize tool call.
        
        Args:
            tool_name: Name of the tool.
            parameters: Tool parameters.
            reasoning: Reasoning for using the tool.
            call_id: Unique call identifier.
        """
        self.tool_name = tool_name
        self.parameters = parameters
        self.reasoning = reasoning
        self.call_id = call_id or f"call_{int(time.time())}"
        self.start_time = time.time()
        self.end_time = None
        self.result = None
        self.success = False
        self.error = None
    
    def mark_completed(self, result: Dict[str, Any], success: bool = True, error: str = None):
        """Mark the tool call as completed.
        
        Args:
            result: Tool execution result.
            success: Whether the call succeeded.
            error: Error message if failed.
        """
        self.end_time = time.time()
        self.result = result
        self.success = success
        self.error = error
    
    @property
    def duration(self) -> float:
        """Get execution duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "call_id": self.call_id,
            "tool_name": self.tool_name,
            "parameters": self.parameters,
            "reasoning": self.reasoning,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "duration": self.duration,
            "success": self.success,
            "result": self.result,
            "error": self.error
        }


class AdvancedToolAgent(BaseAgent):
    """Advanced tool-using agent with full MCP integration."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """Initialize the advanced tool agent.
        
        Args:
            name: Agent name.
            config: Agent configuration.
        """
        super().__init__(name, config)
        self.config = config or {}
        
        # LLM client for reasoning
        self.llm_client = LLMClient()
        self.llm_client.configure_provider(
            self.config.get("provider", "openai"),
            self.config.get("api_key")
        )
        
        # MCP client for tool execution
        mcp_config = self.config.get("mcp", {})
        self.mcp_client = MCPClient(mcp_config)
        
        # Tool execution settings
        self.max_tool_calls = self.config.get("max_tool_calls", 10)
        self.execution_strategy = ToolExecutionStrategy(
            self.config.get("execution_strategy", "sequential")
        )
        self.allow_parallel_execution = self.config.get("allow_parallel_execution", True)
        self.tool_timeout = self.config.get("tool_timeout", 30)
        self.enable_auto_retry = self.config.get("enable_auto_retry", True)
        self.max_retries = self.config.get("max_retries", 3)
        
        # Execution state
        self.available_tools = {}
        self.tool_calls = []
        self.execution_history = []
        self._mcp_initialized = False
        
        # Performance metrics
        self.performance_metrics = {
            "total_tool_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "average_execution_time": 0.0,
            "most_used_tools": {},
            "error_types": {}
        }
    
    def register_tool(self, tool: Dict[str, Any]) -> bool:
        """Register a tool for the agent.
        
        Args:
            tool: Tool definition.
            
        Returns:
            True if successful.
        """
        tool_name = tool.get("name")
        if tool_name:
            self._tools[tool_name] = tool
            return True
        return False
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools.
        
        Returns:
            List of tool definitions.
        """
        return list(self._tools.values())
    
    async def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute task using available tools.
        
        Args:
            task: Task description.
            context: Task context.
            
        Returns:
            Task result with tool usage trace.
        """
        context = context or {}
        self._tool_results = []
        
        tool_calls = self._plan_tool_usage(task, context)
        
        for call in tool_calls[:self.max_tool_calls]:
            result = await self._execute_tool_call(call)
            self._tool_results.append(result)
            
            if result.get("status") == "error":
                break
        
        return {
            "agent": self.name,
            "task": task,
            "tool_calls": self._tool_results,
            "final_answer": self._synthesize_results(task),
            "success": len([r for r in self._tool_results if r.get("status") == "success"]) > 0
        }
    
    def _plan_tool_usage(self, task: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Plan which tools to use for a task.
        
        Args:
            task: Task description.
            context: Task context.
            
        Returns:
            Planned tool calls.
        """
        calls = []
        task_lower = task.lower()
        
        if "read" in task_lower or "file" in task_lower:
            if "read_file" in self._tools:
                calls.append({
                    "tool": "read_file",
                    "parameters": {"filepath": context.get("filepath", "")}
                })
        
        if "write" in task_lower or "create" in task_lower:
            if "write_file" in self._tools:
                calls.append({
                    "tool": "write_file",
                    "parameters": {
                        "filepath": context.get("filepath", ""),
                        "content": context.get("content", "")
                    }
                })
        
        if "search" in task_lower or "find" in task_lower:
            if "search_files" in self._tools:
                calls.append({
                    "tool": "search_files",
                    "parameters": {"pattern": context.get("pattern", "*")}
                })
        
        return calls
    
    async def _execute_tool_call(self, call: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool call.
        
        Args:
            call: Tool call definition.
            
        Returns:
            Tool execution result.
        """
        tool_name = call.get("tool")
        params = call.get("parameters", {})
        
        if tool_name not in self._tools:
            return {
                "tool": tool_name,
                "status": "error",
                "error": f"Tool not found: {tool_name}"
            }
        
        try:
            return {
                "tool": tool_name,
                "parameters": params,
                "status": "success",
                "result": f"Executed {tool_name} with params: {params}"
            }
        except Exception as e:
            return {
                "tool": tool_name,
                "parameters": params,
                "status": "error",
                "error": str(e)
            }
    
    def _synthesize_results(self, task: str) -> str:
        """Synthesize tool results into final answer.
        
        Args:
            task: Original task.
            
        Returns:
            Synthesized answer.
        """
        successful = [r for r in self._tool_results if r.get("status") == "success"]
        
        if not successful:
            return f"Could not complete task: {task}"
        
        return f"Task '{task}' completed using {len(successful)} tool calls."


class ReActAgent(ToolAgent):
    """Agent implementing ReAct (Reasoning + Acting) pattern."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """Initialize the ReAct agent.
        
        Args:
            name: Agent name.
            config: Agent configuration.
        """
        super().__init__(name, config)
        self.max_iterations = config.get("max_iterations", 5) if config else 5
    
    async def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute ReAct reasoning pattern.
        
        Args:
            task: Task description.
            context: Task context.
            
        Returns:
            ReAct execution result.
        """
        context = context or {}
        self._tool_results = []
        
        thought_trace = []
        iteration = 0
        
        while iteration < self.max_iterations:
            iteration += 1
            
            thought = {
                "iteration": iteration,
                "observation": self._get_last_observation(),
                "thought": f"Thinking about how to approach task: {task}",
                "action": None,
                "reasoning": None
            }
            
            action = self._decide_next_action(task, context)
            thought["action"] = action
            
            if action is None:
                thought["reasoning"] = "No more actions needed"
                thought_trace.append(thought)
                break
            
            result = await self._execute_tool_call(action)
            self._tool_results.append(result)
            thought["action_result"] = result
            thought["reasoning"] = f"Executed {action.get('tool')}"
            thought_trace.append(thought)
            
            if self._is_task_complete(task, result):
                break
        
        return {
            "agent": self.name,
            "task": task,
            "reasoning_type": "react",
            "thought_trace": thought_trace,
            "total_iterations": iteration,
            "final_answer": self._synthesize_results(task),
            "success": iteration > 0
        }
    
    def _get_last_observation(self) -> str:
        """Get the last observation from tool execution."""
        if self._tool_results:
            return f"Last result: {self._tool_results[-1]}"
        return "No previous observation"
    
    def _decide_next_action(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Decide the next action to take.
        
        Args:
            task: Current task.
            context: Task context.
            
        Returns:
            Next action or None.
        """
        return self._plan_tool_usage(task, context)[0] if self._plan_tool_usage(task, context) else None
    
    def _is_task_complete(self, task: str, result: Dict[str, Any]) -> bool:
        """Check if task is complete.
        
        Args:
            task: Current task.
            result: Last result.
            
        Returns:
            True if complete.
        """
        return result.get("status") == "success"
