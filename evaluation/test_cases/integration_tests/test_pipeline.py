"""Integration tests for the complete pipeline."""

import pytest


class TestRAGPipeline:
    """Integration tests for RAG pipeline."""
    
    @pytest.fixture
    def pipeline(self):
        """Create a test pipeline."""
        from rag.rag_pipeline import RAGPipeline
        return RAGPipeline()
    
    @pytest.fixture
    def sample_documents(self):
        """Sample documents for testing."""
        return [
            "Python is a programming language.",
            "Machine learning is a subset of AI.",
            "FastAPI is a web framework for Python."
        ]
    
    def test_pipeline_initialization(self, pipeline):
        """Test pipeline initialization."""
        result = pipeline.initialize()
        assert result is True
    
    def test_ingest_documents(self, pipeline, sample_documents):
        """Test document ingestion."""
        result = pipeline.ingest(sample_documents)
        assert result is True
    
    def test_retrieve_documents(self, pipeline):
        """Test document retrieval."""
        results = pipeline.retrieve("Python programming", top_k=2)
        assert isinstance(results, list)


class TestMCPIntegration:
    """Integration tests for MCP integration."""
    
    def test_filesystem_server_creation(self):
        """Test filesystem server creation."""
        from mcp.servers.filesystem.server import FilesystemMCPServer
        
        server = FilesystemMCPServer(root_path="./test_data")
        tools = server.get_tools()
        
        assert len(tools) > 0
        tool_names = [t["name"] for t in tools]
        assert "read_file" in tool_names
        assert "write_file" in tool_names


class TestOrchestration:
    """Integration tests for orchestration."""
    
    def test_orchestrator_creation(self):
        """Test orchestrator creation."""
        from orchestration.orchestrator import Orchestrator
        
        orchestrator = Orchestrator()
        assert orchestrator is not None
    
    def test_workflow_creation(self):
        """Test workflow creation."""
        from orchestration.workflow import Workflow
        
        workflow = Workflow("test_workflow")
        workflow.add_step({"name": "step1", "task": "Test task"})
        
        assert len(workflow._steps) == 1


class TestEvaluation:
    """Integration tests for evaluation."""
    
    def test_evaluator_creation(self):
        """Test evaluator creation."""
        from evaluation.evaluator import Evaluator
        
        evaluator = Evaluator()
        assert evaluator is not None
    
    def test_evaluate_response(self):
        """Test response evaluation."""
        from evaluation.evaluator import Evaluator
        
        evaluator = Evaluator()
        result = evaluator.evaluate(
            prompt="What is Python?",
            response="Python is a programming language.",
            expected="Python is a programming language."
        )
        
        assert "score" in result


class TestFullPipeline:
    """End-to-end integration tests."""
    
    @pytest.fixture
    def setup_full_pipeline(self):
        """Set up the full pipeline for testing."""
        from config.settings import get_settings
        from orchestration.orchestrator import Orchestrator
        
        settings = get_settings()
        orchestrator = Orchestrator()
        
        return orchestrator
    
    def test_execute_simple_prompt(self, setup_full_pipeline):
        """Test executing a simple prompt."""
        orchestrator = setup_full_pipeline
        
        result = orchestrator.execute_prompt(
            skill="general",
            task="Say hello"
        )
        
        assert "result" in result
