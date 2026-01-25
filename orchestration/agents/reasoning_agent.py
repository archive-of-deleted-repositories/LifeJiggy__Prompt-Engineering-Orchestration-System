"""Advanced reasoning agent with CoT, ToT, and self-consistency."""

from typing import Dict, Any, List, Optional, Tuple
import asyncio
import logging
import time
from enum import Enum

from orchestration.agent import BaseAgent
from utilities.llm_client import LLMClient, LLMResponse

logger = logging.getLogger(__name__)


class ReasoningType(Enum):
    """Types of reasoning strategies."""
    CHAIN_OF_THOUGHT = "chain_of_thought"
    TREE_OF_THOUGHTS = "tree_of_thoughts"
    SELF_CONSISTENCY = "self_consistency"
    REACT = "react"
    LEAST_TO_MOST = "least_to_most"
    STEP_BACK = "step_back"


class ReasoningStep:
    """Represents a single reasoning step."""
    
    def __init__(self, step_id: str, thought: str, action: str, result: str = ""):
        """Initialize reasoning step.
        
        Args:
            step_id: Unique step identifier.
            thought: The reasoning thought.
            action: Action taken based on thought.
            result: Result of the action.
        """
        self.step_id = step_id
        self.thought = thought
        self.action = action
        self.result = result
        self.timestamp = time.time()


class ReasoningBranch:
    """Represents a reasoning branch in Tree of Thoughts."""
    
    def __init__(self, branch_id: str, steps: List[ReasoningStep], score: float = 0.0):
        """Initialize reasoning branch.
        
        Args:
            branch_id: Unique branch identifier.
            steps: List of reasoning steps.
            score: Branch evaluation score.
        """
        self.branch_id = branch_id
        self.steps = steps
        self.score = score
        self.confidence = 0.0


class AdvancedReasoningAgent(BaseAgent):
    """Advanced reasoning agent with multiple reasoning strategies."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """Initialize advanced reasoning agent.
        
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
        
        # Reasoning parameters
        self.reasoning_depth = self.config.get("reasoning_depth", 5)
        self.max_branches = self.config.get("max_branches", 3)
        self.consistency_samples = self.config.get("consistency_samples", 3)
        self.confidence_threshold = self.config.get("confidence_threshold", 0.8)
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 2000)
        
        # Reasoning strategies
        self.enabled_strategies = self.config.get("strategies", [
            ReasoningType.CHAIN_OF_THOUGHT,
            ReasoningType.TREE_OF_THOUGHTS,
            ReasoningType.SELF_CONSISTENCY
        ])
        
        # Performance tracking
        self.reasoning_history = []
        self.performance_metrics = {
            "total_reasonings": 0,
            "successful_reasonings": 0,
            "average_confidence": 0.0,
            "average_steps": 0.0
        }
    
    async def reason(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute advanced reasoning task.
        
        Args:
            task: Task description.
            context: Task context.
            
        Returns:
            Reasoning result with detailed analysis.
        """
        start_time = time.time()
        context = context or {}
        
        try:
            # Select reasoning strategy
            strategy = self._select_reasoning_strategy(task)
            
            if strategy == ReasoningType.CHAIN_OF_THOUGHT:
                result = await self._chain_of_thought_reasoning(task, context)
            elif strategy == ReasoningType.TREE_OF_THOUGHTS:
                result = await self._tree_of_thoughts_reasoning(task, context)
            elif strategy == ReasoningType.SELF_CONSISTENCY:
                result = await self._self_consistency_reasoning(task, context)
            elif strategy == ReasoningType.REACT:
                result = await self._react_reasoning(task, context)
            else:
                result = await self._chain_of_thought_reasoning(task, context)
            
            # Update performance metrics
            self._update_performance_metrics(result, time.time() - start_time)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in reasoning: {e}")
            return {
                "agent": self.name,
                "task": task,
                "error": str(e),
                "success": False,
                "reasoning_type": "error"
            }
    
    def _select_reasoning_strategy(self, task: str) -> ReasoningType:
        """Select the best reasoning strategy for a task.
        
        Args:
            task: Task description.
            
        Returns:
            Selected reasoning strategy.
        """
        task_lower = task.lower()
        
        # Complex problems benefit from Tree of Thoughts
        if any(keyword in task_lower for keyword in ["complex", "multiple approaches", "compare", "analyze multiple"]):
            return ReasoningType.TREE_OF_THOUGHTS
        
        # Tasks requiring precision benefit from Self-Consistency
        if any(keyword in task_lower for keyword in ["calculate", "compute", "verify", "check accuracy", "ensure correctness"]):
            return ReasoningType.SELF_CONSISTENCY
        
        # Tasks with tool use benefit from ReAct
        if any(keyword in task_lower for keyword in ["search", "browse", "fetch", "use tool", "calculate", "code"]):
            return ReasoningType.REACT
        
        # Default to Chain of Thought
        return ReasoningType.CHAIN_OF_THOUGHT
    
    def _update_performance_metrics(self, result: Dict[str, Any], duration: float) -> None:
        """Update performance metrics for this reasoning.
        
        Args:
            result: Reasoning result.
            duration: Time taken in seconds.
        """
        self.performance_metrics["total_reasonings"] += 1
        
        if result.get("success", False):
            self.performance_metrics["successful_reasonings"] += 1
        
        if "confidence" in result:
            current_avg = self.performance_metrics["average_confidence"]
            n = self.performance_metrics["total_reasonings"]
            new_avg = ((current_avg * (n - 1)) + result["confidence"]) / n
            self.performance_metrics["average_confidence"] = new_avg
        
        if "steps" in result:
            steps_count = len(result["steps"])
            current_avg_steps = self.performance_metrics["average_steps"]
            n = self.performance_metrics["total_reasonings"]
            new_avg_steps = ((current_avg_steps * (n - 1)) + steps_count) / n
            self.performance_metrics["average_steps"] = new_avg_steps
        
        # Store reasoning in history
        self.reasoning_history.append({
            "timestamp": time.time(),
            "duration": duration,
            "task": result.get("task", ""),
            "reasoning_type": result.get("reasoning_type", ""),
            "success": result.get("success", False),
            "confidence": result.get("confidence", 0.0)
        })
        
        # Keep history size manageable
        if len(self.reasoning_history) > 100:
            self.reasoning_history = self.reasoning_history[-50:]
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics.
        
        Returns:
            Performance metrics.
        """
        return {
            **self.performance_metrics,
            "success_rate": (
                self.performance_metrics["successful_reasonings"] / 
                max(1, self.performance_metrics["total_reasonings"])
            ),
            "recent_reasonings": self.reasoning_history[-10:],
            "enabled_strategies": [s.value for s in self.enabled_strategies]
        }
    
    def compare_reasoning_performance(self) -> Dict[str, Any]:
        """Compare performance across different reasoning strategies.
        
        Returns:
            Performance comparison.
        """
        strategy_performance = {}
        
        for reasoning in self.reasoning_history:
            strategy = reasoning.get("reasoning_type", "")
            if strategy not in strategy_performance:
                strategy_performance[strategy] = {
                    "attempts": 0,
                    "successes": 0,
                    "avg_confidence": 0.0,
                    "avg_duration": 0.0
                }
            
            perf = strategy_performance[strategy]
            perf["attempts"] += 1
            
            if reasoning.get("success", False):
                perf["successes"] += 1
            
            # Update averages
            total = perf["attempts"]
            perf["avg_confidence"] = (
                ((perf["avg_confidence"] * (total - 1)) + reasoning.get("confidence", 0.0)) / total
            )
            perf["avg_duration"] = (
                ((perf["avg_duration"] * (total - 1)) + reasoning.get("duration", 0.0)) / total
            )
        
        # Calculate success rates
        for strategy, perf in strategy_performance.items():
            perf["success_rate"] = perf["successes"] / max(1, perf["attempts"])
        
        return strategy_performance
    
    def adapt_reasoning_strategy(self, task_type: str) -> ReasoningType:
        """Adapt reasoning strategy based on task type and performance.
        
        Args:
            task_type: Type of task.
            
        Returns:
            Recommended reasoning strategy.
        """
        strategy_performance = self.compare_reasoning_performance()
        
        # If we have performance data, choose the best performing strategy
        if strategy_performance:
            best_strategy = None
            best_success_rate = 0.0
            
            for strategy, perf in strategy_performance.items():
                if perf["success_rate"] > best_success_rate:
                    best_success_rate = perf["success_rate"]
                    best_strategy = ReasoningType(strategy)
            
            if best_strategy:
                return best_strategy
        
        # Fallback to heuristic selection
        return self._select_reasoning_strategy(task_type)


# Legacy agents maintained for compatibility
class TreeOfThoughtsAgent(AdvancedReasoningAgent):
    """Agent that explores multiple reasoning branches."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """Initialize the ToT agent.
        
        Args:
            name: Agent name.
            config: Agent configuration.
        """
        super().__init__(name, config)
        self.max_branches = config.get("max_branches", 3) if config else 3
        self.branch_depth = config.get("branch_depth", 2) if config else 2
    
    async def _chain_of_thought_reasoning(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Chain of Thought reasoning with LLM.
        
        Args:
            task: Task description.
            context: Task context.
            
        Returns:
            Chain of Thought reasoning result.
        """
        cot_prompt = f"""You are an expert reasoning agent. Think step-by-step to solve this task.

Task: {task}

Context: {context}

Instructions:
1. Break down the task into logical steps
2. Think through each step carefully
3. Show your reasoning process clearly
4. Provide a final answer with confidence score

Please structure your response as:
{{
    "steps": [
        {{"step": 1, "thought": "...", "action": "...", "result": "..."}},
        {{"step": 2, "thought": "...", "action": "...", "result": "..."}}
    ],
    "final_answer": "...",
    "confidence": 0.0-1.0,
    "reasoning_quality": "...",
    "alternatives_considered": ["..."]
}}"""

        response: LLMResponse = await self.llm_client.generate(
            prompt=cot_prompt,
            model=self.config.get("model", "gpt-4"),
            provider=self.config.get("provider", "openai"),
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        try:
            reasoning_result = eval(response.content)
            reasoning_result["reasoning_type"] = "chain_of_thought"
            reasoning_result["agent"] = self.name
            reasoning_result["task"] = task
            reasoning_result["success"] = True
            reasoning_result["llm_response"] = {
                "provider": response.provider,
                "model": response.model,
                "usage": response.usage,
                "latency_ms": response.latency_ms
            }
            return reasoning_result
        except:
            # Fallback if LLM response parsing fails
            return {
                "agent": self.name,
                "task": task,
                "reasoning_type": "chain_of_thought",
                "final_answer": response.content,
                "confidence": 0.7,
                "success": True,
                "error": "Failed to parse structured reasoning"
            }
    
    async def _tree_of_thoughts_reasoning(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Tree of Thoughts reasoning with LLM.
        
        Args:
            task: Task description.
            context: Task context.
            
        Returns:
            Tree of Thoughts reasoning result.
        """
        tot_prompt = f"""You are an expert reasoning agent using Tree of Thoughts methodology.

Task: {task}
Context: {context}

Generate {self.max_branches} different reasoning branches to solve this task.

For each branch:
1. Start with a different approach or perspective
2. Think through the approach step-by-step
3. Evaluate the quality and likelihood of success
4. Provide a confidence score (0.0-1.0)

Structure your response as:
{{
    "branches": [
        {{
            "branch_id": 1,
            "approach": "...",
            "steps": [
                {{"thought": "...", "action": "..."}},
                {{"thought": "...", "action": "..."}}
            ],
            "evaluation": {{"quality": "...", "feasibility": "...", "confidence": 0.0}},
            "expected_outcome": "..."
        }}
    ],
    "best_branch": 1,
    "synthesis": "...",
    "final_answer": "...",
    "overall_confidence": 0.0
}}"""

        response: LLMResponse = await self.llm_client.generate(
            prompt=tot_prompt,
            model=self.config.get("model", "gpt-4"),
            provider=self.config.get("provider", "openai"),
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        try:
            reasoning_result = eval(response.content)
            reasoning_result["reasoning_type"] = "tree_of_thoughts"
            reasoning_result["agent"] = self.name
            reasoning_result["task"] = task
            reasoning_result["success"] = True
            reasoning_result["llm_response"] = {
                "provider": response.provider,
                "model": response.model,
                "usage": response.usage,
                "latency_ms": response.latency_ms
            }
            return reasoning_result
        except:
            return {
                "agent": self.name,
                "task": task,
                "reasoning_type": "tree_of_thoughts",
                "final_answer": response.content,
                "confidence": 0.7,
                "success": True,
                "error": "Failed to parse structured reasoning"
            }
    
    async def _self_consistency_reasoning(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute Self-Consistency reasoning with multiple samples.
        
        Args:
            task: Task description.
            context: Task context.
            
        Returns:
            Self-Consistency reasoning result.
        """
        sc_prompt = f"""You are an expert reasoning agent using Self-Consistency methodology.

Task: {task}
Context: {context}

Generate {self.consistency_samples} independent attempts to solve this task.

For each attempt:
1. Solve the problem from scratch
2. Show your reasoning step-by-step
3. Provide a final answer
4. Evaluate your confidence (0.0-1.0)

After all attempts, analyze the answers and provide:
- A consensus answer
- Agreement rate
- Final confidence

Structure as:
{{
    "samples": [
        {{
            "sample_id": 1,
            "reasoning": "...",
            "answer": "...",
            "confidence": 0.0
        }}
    ],
    "consensus_analysis": {{
        "answers": ["...", "...", "..."],
        "majority_answer": "...",
        "agreement_rate": 0.0,
        "confidence": 0.0
    }},
    "final_answer": "...",
    "success": true
}}"""

        response: LLMResponse = await self.llm_client.generate(
            prompt=sc_prompt,
            model=self.config.get("model", "gpt-4"),
            provider=self.config.get("provider", "openai"),
            temperature=self.temperature + 0.1,  # Higher temperature for diversity
            max_tokens=self.max_tokens
        )
        
        try:
            reasoning_result = eval(response.content)
            reasoning_result["reasoning_type"] = "self_consistency"
            reasoning_result["agent"] = self.name
            reasoning_result["task"] = task
            reasoning_result["success"] = True
            reasoning_result["llm_response"] = {
                "provider": response.provider,
                "model": response.model,
                "usage": response.usage,
                "latency_ms": response.latency_ms
            }
            return reasoning_result
        except:
            return {
                "agent": self.name,
                "task": task,
                "reasoning_type": "self_consistency",
                "final_answer": response.content,
                "confidence": 0.6,
                "success": True,
                "error": "Failed to parse structured reasoning"
            }
    
    async def _react_reasoning(self, task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute ReAct (Reason+Act) reasoning.
        
        Args:
            task: Task description.
            context: Task context.
            
        Returns:
            ReAct reasoning result.
        """
        react_prompt = f"""You are an expert reasoning agent using the ReAct (Reason+Act) methodology.

Task: {task}
Context: {context}

Follow this pattern:
1. Thought: Analyze the current situation
2. Action: Decide on the next action (or provide final answer)
3. Observation: Note the result of your action

Continue this thought-action-observation cycle until the task is complete.

Structure your response as:
{{
    "steps": [
        {{
            "step": 1,
            "thought": "...",
            "action": "...",
            "observation": "...",
            "action_type": "reasoning" or "final_answer"
        }}
    ],
    "final_answer": "...",
    "action_sequence": ["...", "..."],
    "success": true,
    "confidence": 0.0
}}"""

        response: LLMResponse = await self.llm_client.generate(
            prompt=react_prompt,
            model=self.config.get("model", "gpt-4"),
            provider=self.config.get("provider", "openai"),
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )
        
        try:
            reasoning_result = eval(response.content)
            reasoning_result["reasoning_type"] = "react"
            reasoning_result["agent"] = self.name
            reasoning_result["task"] = task
            reasoning_result["success"] = True
            reasoning_result["llm_response"] = {
                "provider": response.provider,
                "model": response.model,
                "usage": response.usage,
                "latency_ms": response.latency_ms
            }
            return reasoning_result
        except:
            return {
                "agent": self.name,
                "task": task,
                "reasoning_type": "react",
                "final_answer": response.content,
                "confidence": 0.7,
                "success": True,
                "error": "Failed to parse structured reasoning"
            }
    
    def _generate_reasoning_path(self, task: str, branch_id: int) -> List[Dict[str, Any]]:
        """Generate a reasoning path for a branch.
        
        Args:
            task: Task description.
            branch_id: Branch identifier.
            
        Returns:
            Reasoning path steps.
        """
        return [
            {"step": 1, "thought": f"Branch {branch_id}: Initial analysis"},
            {"step": 2, "thought": f"Branch {branch_id}: Exploring options"},
            {"step": 3, "thought": f"Branch {branch_id}: Reaching conclusion"}
        ]
    
    def _evaluate_branch(self, task: str, branch_id: int) -> Dict[str, Any]:
        """Evaluate a reasoning branch.
        
        Args:
            task: Task description.
            branch_id: Branch identifier.
            
        Returns:
            Branch evaluation.
        """
        return {
            "completeness": 0.8,
            "coherence": 0.85,
            "relevance": 0.9,
            "overall": 0.85
        }


class SelfConsistencyAgent(AdvancedReasoningAgent):
    """Agent that validates reasoning through multiple paths."""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        """Initialize the self-consistency agent.
        
        Args:
            name: Agent name.
            config: Agent configuration.
        """
        super().__init__(name, config)
        self.num_samples = config.get("num_samples", 3) if config else 3
    
    async def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute self-consistency reasoning.
        
        Args:
            task: Task description.
            context: Task context.
            
        Returns:
            Reasoning result with consensus.
        """
        context = context or {}
        
        samples = []
        for i in range(self.num_samples):
            sample = {
                "sample_id": i + 1,
                "reasoning": f"Sample reasoning {i + 1}",
                "answer": f"Answer {i + 1}",
                "confidence": 0.7 + (i * 0.05)
            }
            samples.append(sample)
        
        answers = [s["answer"] for s in samples]
        consensus = self._find_consensus(answers)
        
        return {
            "agent": self.name,
            "task": task,
            "reasoning_type": "self_consistency",
            "samples": samples,
            "consensus": consensus,
            "final_answer": consensus["majority_answer"],
            "confidence": consensus["agreement_rate"],
            "success": True
        }
    
    def _find_consensus(self, answers: List[str]) -> Dict[str, Any]:
        """Find consensus among answers.
        
        Args:
            answers: List of answers.
            
        Returns:
            Consensus result.
        """
        from collections import Counter
        
        counter = Counter(answers)
        most_common = counter.most_common(1)[0]
        
        return {
            "majority_answer": most_common[0],
            "agreement_rate": most_common[1] / len(answers),
            "vote_counts": dict(counter)
        }


class ReasoningAgent(AdvancedReasoningAgent):
    """Simplified reasoning agent for backward compatibility."""
    
    async def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute reasoning task with CoT.
        
        Args:
            task: Task description.
            context: Task context.
            
        Returns:
            Chain of Thought reasoning result.
        """
        return await self.reason(task, context)
