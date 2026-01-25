"""Sequential workflow implementation."""

from typing import Dict, Any, List, Optional
from orchestration.workflow import Workflow


class SequentialWorkflow(Workflow):
    """Executes steps sequentially."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """Initialize the sequential workflow.
        
        Args:
            name: Workflow name.
            config: Workflow configuration.
        """
        super().__init__(name, config)
        self._results = []
    
    async def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute workflow steps sequentially.
        
        Args:
            params: Workflow parameters.
            
        Returns:
            Combined results from all steps.
        """
        params = params or {}
        results = []
        current_result = {}
        
        for i, step in enumerate(self._steps):
            step_name = step.get("name", f"step_{i}")
            step_task = step.get("task", "")
            step_params = step.get("params", {})
            
            merged_params = {**params, **current_result, **step_params}
            
            if "agent" in step:
                agent = step["agent"]
                result = await agent.run(step_task, merged_params)
            elif "tool" in step:
                tool = step["tool"]
                result = await self._execute_tool(tool, merged_params)
            else:
                result = {"step": step_name, "output": f"Task: {step_task}"}
            
            step_result = {
                "step": step_name,
                "step_index": i,
                "result": result,
                "success": result.get("success", True)
            }
            
            results.append(step_result)
            current_result = result
            
            if not step_result["success"] and step.get("stop_on_error", True):
                break
        
        return {
            "workflow": self.name,
            "total_steps": len(results),
            "completed_steps": len([r for r in results if r["success"]]),
            "results": results,
            "final_result": current_result
        }
    
    async def _execute_tool(
        self,
        tool: Dict[str, Any],
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool.
        
        Args:
            tool: Tool definition.
            params: Tool parameters.
            
        Returns:
            Tool execution result.
        """
        return {"tool": tool.get("name"), "params": params, "success": True}
