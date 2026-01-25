"""Coordinator agent for multi-agent orchestration."""

from typing import Dict, Any, List, Optional
from orchestration.agent import BaseAgent


class CoordinatorAgent(BaseAgent):
    """Agent that coordinates other agents for complex tasks."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """Initialize the coordinator agent.
        
        Args:
            name: Agent name.
            config: Agent configuration.
        """
        super().__init__(name, config)
        self._agents = []
        self._task_queue = []
        self._results = []
    
    def register_agent(self, agent: BaseAgent) -> bool:
        """Register an agent for coordination.
        
        Args:
            agent: Agent to register.
            
        Returns:
            True if successful.
        """
        self._agents.append(agent)
        return True
    
    def list_agents(self) -> List[str]:
        """List registered agents.
        
        Returns:
            List of agent names.
        """
        return [agent.name for agent in self._agents]
    
    async def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Coordinate agents to complete a complex task.
        
        Args:
            task: Task description.
            context: Task context.
            
        Returns:
            Coordinated result.
        """
        context = context or {}
        self._task_queue = []
        self._results = []
        
        subtasks = self._decompose_into_subtasks(task)
        
        for subtask in subtasks:
            agent = self._select_agent(subtask)
            
            if agent:
                result = await agent.run(subtask, context)
                self._results.append({
                    "subtask": subtask,
                    "agent": agent.name,
                    "result": result
                })
        
        synthesis = self._synthesize_results(task)
        
        return {
            "agent": self.name,
            "task": task,
            "coordination_type": "centralized",
            "subtasks": len(subtasks),
            "agent_assignments": self._results,
            "final_answer": synthesis,
            "success": len(self._results) > 0
        }
    
    def _decompose_into_subtasks(self, task: str) -> List[str]:
        """Decompose a task into subtasks.
        
        Args:
            task: Complex task.
            
        Returns:
            List of subtasks.
        """
        subtasks = []
        
        if "analyze" in task.lower():
            subtasks.append("Analyze the requirements")
        if "design" in task.lower():
            subtasks.append("Design the solution")
        if "implement" in task.lower() or "build" in task.lower():
            subtasks.append("Implement the solution")
        if "test" in task.lower():
            subtasks.append("Test the implementation")
        if "review" in task.lower():
            subtasks.append("Review and refine")
        
        if not subtasks:
            subtasks = [
                "Gather information",
                "Process information",
                "Formulate response"
            ]
        
        return subtasks
    
    def _select_agent(self, subtask: str) -> Optional[BaseAgent]:
        """Select the best agent for a subtask.
        
        Args:
            subtask: Subtask description.
            
        Returns:
            Selected agent or None.
        """
        subtask_lower = subtask.lower()
        
        agent_scores = []
        for agent in self._agents:
            score = 0
            agent_name_lower = agent.name.lower()
            
            if "code" in subtask_lower or "implement" in subtask_lower:
                if "coding" in agent_name_lower or "tool" in agent_name_lower:
                    score = 10
            if "reason" in subtask_lower or "analyze" in subtask_lower:
                if "reasoning" in agent_name_lower:
                    score = 10
            if "write" in subtask_lower or "create" in subtask_lower:
                if "writing" in agent_name_lower:
                    score = 10
            
            if score == 0:
                score = 5
            
            agent_scores.append((agent, score))
        
        agent_scores.sort(key=lambda x: x[1], reverse=True)
        
        return agent_scores[0][0] if agent_scores else None
    
    def _synthesize_results(self, task: str) -> str:
        """Synthesize results from all agents.
        
        Args:
            task: Original task.
            
        Returns:
            Synthesized answer.
        """
        successful = [r for r in self._results if r.get("result", {}).get("success", False)]
        
        return f"Task '{task}' coordinated across {len(self._agents)} agents with {len(successful)} successful subtasks."


class HierarchicalCoordinator(CoordinatorAgent):
    """Hierarchical multi-level coordinator."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """Initialize hierarchical coordinator.
        
        Args:
            name: Coordinator name.
            config: Configuration.
        """
        super().__init__(name, config)
        self._levels = {}
        self._current_level = 0
    
    def add_level(self, level: int, agents: List[BaseAgent]) -> None:
        """Add agents at a specific level.
        
        Args:
            level: Hierarchical level.
            agents: Agents at this level.
        """
        self._levels[level] = agents
    
    async def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute hierarchical coordination.
        
        Args:
            task: Task description.
            context: Task context.
            
        Returns:
            Hierarchical coordination result.
        """
        context = context or {}
        
        level_results = {}
        
        for level in sorted(self._levels.keys()):
            agents = self._levels[level]
            level_output = []
            
            for agent in agents:
                result = await agent.run(task, context)
                level_output.append({
                    "agent": agent.name,
                    "result": result
                })
            
            level_results[f"level_{level}"] = level_output
        
        return {
            "agent": self.name,
            "task": task,
            "coordination_type": "hierarchical",
            "levels": level_results,
            "final_answer": f"Hierarchical coordination complete across {len(self._levels)} levels",
            "success": True
        }
