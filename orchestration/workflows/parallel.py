"""Parallel workflow implementation."""

from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from orchestration.workflow import Workflow


class ParallelWorkflow(Workflow):
    """Executes steps in parallel."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """Initialize the parallel workflow.
        
        Args:
            name: Workflow name.
            config: Workflow configuration.
        """
        super().__init__(name, config)
        self._max_workers = config.get("max_workers", 4) if config else 4
    
    def set_max_workers(self, max_workers: int) -> None:
        """Set maximum parallel workers.
        
        Args:
            max_workers: Maximum number of workers.
        """
        self._max_workers = max_workers
    
    async def execute(self, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute workflow steps in parallel.
        
        Args:
            params: Workflow parameters.
            
        Returns:
            Combined results from all steps.
        """
        params = params or {}
        
        async def run_step(step: Dict, idx: int) -> Dict[str, Any]:
            step_name = step.get("name", f"step_{idx}")
            step_task = step.get("task", "")
            step_params = step.get("params", {})
            
            merged_params = {**params, **step_params}
            
            if "agent" in step:
                agent = step["agent"]
                result = await agent.run(step_task, merged_params)
            elif "tool" in step:
                tool = step["tool"]
                result = await self._execute_tool(tool, merged_params)
            else:
                result = {"step": step_name, "output": f"Task: {step_task}"}
            
            return {
                "step": step_name,
                "step_index": idx,
                "result": result,
                "success": result.get("success", True)
            }
        
        import asyncio
        
        tasks = [run_step(step, idx) for idx, step in enumerate(self._steps)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    "step": self._steps[i].get("name", f"step_{i}"),
                    "step_index": i,
                    "result": {"error": str(result)},
                    "success": False
                })
            else:
                processed_results.append(result)
        
        return {
            "workflow": self.name,
            "total_steps": len(processed_results),
            "completed_steps": len([r for r in processed_results if r["success"]]),
            "results": processed_results,
            "execution_mode": "parallel",
            "max_workers": self._max_workers
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
