"""Orchestrator for managing AI agents and workflows."""

import asyncio
from typing import Dict, Any, Optional
import logging

from utilities.llm_client import LLMClient, ModelProvider, LLMResponse
from config.settings import get_settings

logger = logging.getLogger(__name__)


class Orchestrator:
    """Main orchestrator for AI operations."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the orchestrator.
        
        Args:
            config: Orchestrator configuration.
        """
        self.config = config or {}
        self.llm_client = LLMClient()
        self._setup_providers()
    
    def _setup_providers(self) -> None:
        """Configure LLM providers from settings."""
        settings = get_settings()
        
        if settings.api.openai_api_key:
            self.llm_client.configure_provider(
                ModelProvider.OPENAI,
                settings.api.openai_api_key
            )
            logger.info("Configured OpenAI provider")
        
        if settings.api.anthropic_api_key:
            self.llm_client.configure_provider(
                ModelProvider.ANTHROPIC,
                settings.api.anthropic_api_key
            )
            logger.info("Configured Anthropic provider")
        
        if settings.api.google_api_key:
            self.llm_client.configure_provider(
                ModelProvider.GOOGLE,
                settings.api.google_api_key
            )
            logger.info("Configured Google provider")
    
    async def execute_prompt(
        self,
        skill: str,
        task: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a prompt with a specific skill.
        
        Args:
            skill: Skill to use.
            task: Task description.
            context: Optional context.
            
        Returns:
            Execution result.
        """
        try:
            prompt = self._build_skill_prompt(skill, task, context)
            
            provider = self.config.get("provider", "openai")
            model = self.config.get("model", "gpt-4")
            temperature = self.config.get("temperature", 0.7)
            
            response: LLMResponse = await self.llm_client.generate(
                prompt=prompt,
                model=model,
                provider=provider,
                temperature=temperature
            )
            
            return {
                "result": response.content,
                "provider": response.provider,
                "model": response.model,
                "usage": response.usage,
                "latency_ms": response.latency_ms,
                "finish_reason": response.finish_reason,
                "skill": skill,
                "task": task
            }
        except Exception as e:
            logger.error(f"Error executing prompt: {e}")
            return {
                "result": None,
                "error": str(e),
                "skill": skill,
                "task": task
            }
    
    def _build_skill_prompt(
        self,
        skill: str,
        task: str,
        context: Dict[str, Any] = None
    ) -> str:
        """Build a prompt for the given skill and task.
        
        Args:
            skill: Skill name.
            task: Task description.
            context: Optional context.
            
        Returns:
            Formatted prompt.
        """
        base_prompt = f"Skill: {skill}\nTask: {task}"
        
        if context:
            if "documents" in context:
                docs_text = "\n".join([
                    f"[Document {i+1}]: {doc[:500]}" 
                    for i, doc in enumerate(context["documents"][:5])
                ])
                base_prompt += f"\n\nRelevant Context:\n{docs_text}"
            
            if "conversation_history" in context:
                history = context["conversation_history"][-10:]
                history_text = "\n".join([
                    f"{msg['role']}: {msg['content'][:200]}"
                    for msg in history
                ])
                base_prompt += f"\\n\nConversation History:\n{history_text}"
        
        base_prompt += "\n\nPlease provide a helpful response:"
        return base_prompt
    
    async def execute_workflow(
        self,
        workflow: Dict[str, Any],
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Execute a workflow.
        
        Args:
            workflow: Workflow definition.
            params: Workflow parameters.
            
        Returns:
            Workflow result.
        """
        try:
            params = params or {}
            workflow_type = workflow.get("type", "sequential")
            steps = workflow.get("steps", [])
            
            if not steps:
                return {"result": None, "error": "No steps defined in workflow"}
            
            results = []
            
            if workflow_type == "sequential":
                for step in steps:
                    step_result = await self._execute_step(step, params, results)
                    results.append(step_result)
            
            elif workflow_type == "parallel":
                tasks = [
                    self._execute_step(step, params, results)
                    for step in steps
                ]
                results = await asyncio.gather(*tasks)
            
            return {
                "result": results,
                "workflow_type": workflow_type,
                "steps_count": len(steps),
                "completed": True
            }
        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            return {"result": None, "error": str(e)}
    
    async def _execute_step(
        self,
        step: Dict[str, Any],
        params: Dict[str, Any],
        previous_results: list
    ) -> Dict[str, Any]:
        """Execute a single workflow step.
        
        Args:
            step: Step definition.
            params: Workflow parameters.
            previous_results: Results from previous steps.
            
        Returns:
            Step result.
        """
        step_type = step.get("type", "prompt")
        
        if step_type == "prompt":
            skill = step.get("skill", "general")
            task = step.get("task", "")
            
            task = self._render_template(task, params, previous_results)
            
            context = step.get("context", {})
            if previous_results:
                context["previous_results"] = previous_results
            
            return await self.execute_prompt(skill, task, context)
        
        elif step_type == "condition":
            condition = step.get("condition", "")
            true_branch = step.get("true_branch", [])
            false_branch = step.get("false_branch", [])
            
            condition_result = self._evaluate_condition(condition, params, previous_results)
            
            if condition_result:
                branch = true_branch
            else:
                branch = false_branch
            
            branch_results = []
            for step_def in branch:
                step_result = await self._execute_step(step_def, params, previous_results + branch_results)
                branch_results.append(step_result)
            
            return {"condition": condition, "result": condition_result, "branch_results": branch_results}
        
        return {"step_type": step_type, "result": "Skipped"}
    
    def _render_template(
        self,
        template: str,
        params: Dict[str, Any],
        results: list
    ) -> str:
        """Render a template with parameters.
        
        Args:
            template: Template string.
            params: Parameters to substitute.
            results: Previous results.
            
        Returns:
            Rendered string.
        """
        rendered = template
        
        for key, value in params.items():
            placeholder = f"{{{{ {key} }}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        if results:
            rendered = rendered.replace("{{ previous_result }}", str(results[-1]))
        
        return rendered
    
    def _evaluate_condition(
        self,
        condition: str,
        params: Dict[str, Any],
        results: list
    ) -> bool:
        """Evaluate a condition expression.
        
        Args:
            condition: Condition expression.
            params: Parameters.
            results: Previous results.
            
        Returns:
            Boolean result.
        """
        try:
            context = {**params}
            if results:
                context["last_result"] = results[-1]
            
            return bool(eval(condition, {"__builtins__": {}}, context))
        except Exception:
            return False
    
    async def query_with_rag(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        """Query with RAG augmentation.
        
        Args:
            query: Query string.
            top_k: Number of results.
            
        Returns:
            RAG query result.
        """
        try:
            from rag.pipelines.retrieval_pipeline import RetrievalPipeline
            
            retriever = RetrievalPipeline()
            retrieved_docs = await retriever.retrieve(
                query=query,
                top_k=top_k
            )
            
            context_texts = [
                doc.get("content", doc.get("text", str(doc)))
                for doc in retrieved_docs
            ]
            
            rag_prompt = f"""Based on the following context, please answer the query.

Context:
{chr(10).join(context_texts)}

Query: {query}

Please provide a helpful and accurate response based on the context above:"""
            
            provider = self.config.get("provider", "openai")
            model = self.config.get("model", "gpt-4")
            
            response: LLMResponse = await self.llm_client.generate(
                prompt=rag_prompt,
                model=model,
                provider=provider,
                temperature=0.3
            )
            
            return {
                "result": response.content,
                "provider": response.provider,
                "model": response.model,
                "usage": response.usage,
                "retrieved_documents": len(retrieved_docs),
                "query": query
            }
        except ImportError as e:
            logger.warning(f"RAG pipeline not available: {e}")
            return {
                "result": None,
                "error": "RAG pipeline not configured",
                "query": query
            }
        except Exception as e:
            logger.error(f"Error in RAG query: {e}")
            return {"result": None, "error": str(e), "query": query}
    
    async def stream_prompt(
        self,
        skill: str,
        task: str,
        context: Dict[str, Any] = None
    ):
        """Stream a prompt response.
        
        Args:
            skill: Skill to use.
            task: Task description.
            context: Optional context.
            
        Yields:
            Stream chunks.
        """
        prompt = self._build_skill_prompt(skill, task, context)
        
        provider = self.config.get("provider", "openai")
        model = self.config.get("model", "gpt-4")
        
        async for chunk in self.llm_client.stream_generate(
            prompt=prompt,
            model=model,
            provider=provider
        ):
            yield chunk
