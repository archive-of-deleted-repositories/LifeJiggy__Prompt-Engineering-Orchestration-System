"""
Advanced Prompt Engineering Orchestration System
Main application entry point.
"""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog

from config.settings import get_settings
from config.feature_flags import get_feature_manager
from orchestration.orchestrator import Orchestrator

structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(get_settings().monitoring.log_level),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    logger.info("Starting Advanced Prompt Engineering Orchestration System")
    
    settings = get_settings()
    feature_manager = get_feature_manager()
    
    logger.info(
        "Configuration loaded",
        environment=settings.environment,
        debug=settings.debug,
    )
    
    enabled_features = feature_manager.get_enabled()
    logger.info("Enabled features", features=enabled_features)
    
    yield
    
    logger.info("Shutting down system")


app = FastAPI(
    title="Advanced Prompt Engineering Orchestration System",
    description="A production-ready platform for advanced prompt engineering with RAG, MCP integration, and agent orchestration.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors.allow_origins if hasattr(settings, 'cors') else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
    }


@app.get("/api/v1/features")
async def list_features():
    """List all available features and their status."""
    feature_manager = get_feature_manager()
    return feature_manager.get_all()


@app.get("/api/v1/models")
async def list_models():
    """List available models."""
    from config.config_loader import get_config_loader
    
    loader = get_config_loader()
    models = loader.load_models()
    
    return {
        "models": [
            {
                "name": name,
                "provider": config.provider,
                "capabilities": config.capabilities,
            }
            for name, config in models.items()
        ]
    }


@app.post("/api/v1/prompts/execute")
async def execute_prompt(request: Request):
    """Execute a prompt with a specific skill."""
    body = await request.json()
    
    skill = body.get("skill", "general")
    task = body.get("task", "")
    context = body.get("context", {})
    
    result = await orchestrator.execute_prompt(skill=skill, task=task, context=context)
    
    return result


@app.post("/api/v1/rag/query")
async def query_rag(request: Request):
    """Query with RAG augmentation."""
    body = await request.json()
    
    query = body.get("query", "")
    top_k = body.get("top_k", 5)
    
    result = await orchestrator.query_with_rag(query=query, top_k=top_k)
    
    return result


@app.post("/api/v1/workflows/execute")
async def execute_workflow(request: Request):
    """Execute a workflow."""
    body = await request.json()
    
    workflow = body.get("workflow", {})
    params = body.get("params", {})
    
    result = await orchestrator.execute_workflow(workflow=workflow, params=params)
    
    return result


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler."""
    logger.error("Unhandled exception", error=str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)},
    )


if __name__ == "__main__":
    import uvicorn
    
    settings = get_settings()
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.monitoring.log_level.lower(),
    )
