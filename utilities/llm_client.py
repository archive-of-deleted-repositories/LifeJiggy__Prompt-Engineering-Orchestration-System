"""LLM client for making API calls to various providers."""

import asyncio
from typing import Dict, Any, List, Optional, AsyncIterator
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"


@dataclass
class LLMResponse:
    """Response from LLM API."""
    content: str
    provider: str
    model: str
    usage: Dict[str, int]
    latency_ms: float
    finish_reason: str


@dataclass
class StreamChunk:
    """Streaming response chunk."""
    content: str
    provider: str
    model: str
    done: bool


class LLMClient:
    """Unified LLM client supporting multiple providers."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the LLM client.
        
        Args:
            config: Client configuration.
        """
        self.config = config or {}
        self._clients: Dict[ModelProvider, Any] = {}
        self._default_provider = ModelProvider.OPENAI
    
    def configure_provider(
        self,
        provider: ModelProvider,
        api_key: str,
        **kwargs
    ) -> None:
        """Configure a specific provider.
        
        Args:
            provider: Provider to configure.
            api_key: API key for the provider.
            **kwargs: Additional provider options.
        """
        if provider == ModelProvider.OPENAI:
            self._clients[provider] = OpenAIClient(api_key, **kwargs)
        elif provider == ModelProvider.ANTHROPIC:
            self._clients[provider] = AnthropicClient(api_key, **kwargs)
        elif provider == ModelProvider.GOOGLE:
            self._clients[provider] = GoogleClient(api_key, **kwargs)
    
    async def generate(
        self,
        prompt: str,
        model: str = "gpt-4",
        provider: str = "openai",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """Generate response from LLM.
        
        Args:
            prompt: Input prompt.
            model: Model to use.
            provider: Provider name.
            temperature: Temperature setting.
            max_tokens: Maximum output tokens.
            stream: Whether to stream response.
            **kwargs: Additional options.
            
        Returns:
            LLM response.
        """
        provider_enum = ModelProvider(provider)
        client = self._clients.get(provider_enum)
        
        if not client:
            logger.warning(f"Provider {provider} not configured, using default")
            client = self._clients.get(self._default_provider)
        
        if not client:
            return LLMResponse(
                content="Error: No LLM provider configured",
                provider=provider,
                model=model,
                usage={"input_tokens": 0, "output_tokens": 0},
                latency_ms=0,
                finish_reason="error"
            )
        
        return await client.generate(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            **kwargs
        )
    
    async def stream_generate(
        self,
        prompt: str,
        model: str = "gpt-4",
        provider: str = "openai",
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Generate streaming response.
        
        Args:
            prompt: Input prompt.
            model: Model to use.
            provider: Provider name.
            temperature: Temperature setting.
            **kwargs: Additional options.
            
        Yields:
            Stream chunks.
        """
        provider_enum = ModelProvider(provider)
        client = self._clients.get(provider_enum)
        
        if client:
            async for chunk in client.stream_generate(
                prompt=prompt,
                model=model,
                temperature=temperature,
                **kwargs
            ):
                yield chunk


class BaseClient:
    """Base class for provider clients."""
    
    async def generate(
        self,
        prompt: str,
        model: str,
        temperature: float,
        max_tokens: int,
        stream: bool,
        **kwargs
    ) -> LLMResponse:
        """Generate response. Override in subclass."""
        raise NotImplementedError
    
    async def stream_generate(
        self,
        prompt: str,
        model: str,
        temperature: float,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Generate streaming response. Override in subclass."""
        raise NotImplementedError


class OpenAIClient(BaseClient):
    """OpenAI API client."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key.
            **kwargs: Additional options.
        """
        self.api_key = api_key
        self.base_url = kwargs.get("base_url", "https://api.openai.com/v1")
    
    async def generate(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """Generate response using OpenAI API.
        
        Args:
            prompt: Input prompt.
            model: Model name.
            temperature: Temperature setting.
            max_tokens: Maximum output tokens.
            stream: Whether to stream.
            **kwargs: Additional options.
            
        Returns:
            LLM response.
        """
        import time
        start_time = time.time()
        
        try:
            import httpx
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=120.0
                )
                response.raise_for_status()
                data = response.json()
                
                latency_ms = (time.time() - start_time) * 1000
                
                choice = data["choices"][0]
                content = choice["message"]["content"]
                usage = data.get("usage", {})
                
                return LLMResponse(
                    content=content,
                    provider="openai",
                    model=model,
                    usage={
                        "input_tokens": usage.get("prompt_tokens", 0),
                        "output_tokens": usage.get("completion_tokens", 0)
                    },
                    latency_ms=latency_ms,
                    finish_reason=choice.get("finish_reason", "stop")
                )
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return LLMResponse(
                content=f"Error: {str(e)}",
                provider="openai",
                model=model,
                usage={"input_tokens": 0, "output_tokens": 0},
                latency_ms=0,
                finish_reason="error"
            )
    
    async def stream_generate(
        self,
        prompt: str,
        model: str = "gpt-4",
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Generate streaming response."""
        import httpx
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "stream": True
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=120.0
            ) as response:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data != "[DONE]":
                            import json
                            chunk_data = json.loads(data)
                            choice = chunk_data["choices"][0]
                            content = choice["delta"].get("content", "")
                            done = choice.get("finish_reason") is not None
                            
                            yield StreamChunk(
                                content=content,
                                provider="openai",
                                model=model,
                                done=done
                            )


class AnthropicClient(BaseClient):
    """Anthropic API client."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize Anthropic client.
        
        Args:
            api_key: Anthropic API key.
            **kwargs: Additional options.
        """
        self.api_key = api_key
        self.base_url = kwargs.get("base_url", "https://api.anthropic.com")
    
    async def generate(
        self,
        prompt: str,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Anthropic API.
        
        Args:
            prompt: Input prompt.
            model: Model name.
            temperature: Temperature setting.
            max_tokens: Maximum output tokens.
            stream: Whether to stream.
            **kwargs: Additional options.
            
        Returns:
            LLM response.
        """
        import time
        start_time = time.time()
        
        try:
            import httpx
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            payload = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
                "max_tokens": max_tokens,
                "stream": stream
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/v1/messages",
                    headers=headers,
                    json=payload,
                    timeout=120.0
                )
                response.raise_for_status()
                data = response.json()
                
                latency_ms = (time.time() - start_time) * 1000
                
                content = data["content"][0]["text"]
                usage = data.get("usage", {})
                
                return LLMResponse(
                    content=content,
                    provider="anthropic",
                    model=model,
                    usage={
                        "input_tokens": usage.get("input_tokens", 0),
                        "output_tokens": usage.get("output_tokens", 0)
                    },
                    latency_ms=latency_ms,
                    finish_reason="stop"
                )
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            return LLMResponse(
                content=f"Error: {str(e)}",
                provider="anthropic",
                model=model,
                usage={"input_tokens": 0, "output_tokens": 0},
                latency_ms=0,
                finish_reason="error"
            )
    
    async def stream_generate(
        self,
        prompt: str,
        model: str = "claude-3-sonnet-20240229",
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Generate streaming response."""
        yield StreamChunk(content="", provider="anthropic", model=model, done=False)


class GoogleClient(BaseClient):
    """Google API client."""
    
    def __init__(self, api_key: str, **kwargs):
        """Initialize Google client.
        
        Args:
            api_key: Google API key.
            **kwargs: Additional options.
        """
        self.api_key = api_key
        self.base_url = kwargs.get("base_url", "https://generativelanguage.googleapis.com/v1beta")
    
    async def generate(
        self,
        prompt: str,
        model: str = "gemini-pro",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        stream: bool = False,
        **kwargs
    ) -> LLMResponse:
        """Generate response using Google API.
        
        Args:
            prompt: Input prompt.
            model: Model name.
            temperature: Temperature setting.
            max_tokens: Maximum output tokens.
            stream: Whether to stream.
            **kwargs: Additional options.
            
        Returns:
            LLM response.
        """
        import time
        start_time = time.time()
        
        try:
            import httpx
            
            url = f"{self.base_url}/models/{model}:generateContent"
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens
                }
            }
            
            params = {"key": self.api_key}
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    params=params,
                    json=payload,
                    timeout=120.0
                )
                response.raise_for_status()
                data = response.json()
                
                latency_ms = (time.time() - start_time) * 1000
                
                content = data["candidates"][0]["content"]["parts"][0]["text"]
                
                return LLMResponse(
                    content=content,
                    provider="google",
                    model=model,
                    usage={"input_tokens": 0, "output_tokens": 0},
                    latency_ms=latency_ms,
                    finish_reason="stop"
                )
        except Exception as e:
            logger.error(f"Google API error: {e}")
            return LLMResponse(
                content=f"Error: {str(e)}",
                provider="google",
                model=model,
                usage={"input_tokens": 0, "output_tokens": 0},
                latency_ms=0,
                finish_reason="error"
            )
    
    async def stream_generate(
        self,
        prompt: str,
        model: str = "gemini-pro",
        temperature: float = 0.7,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """Generate streaming response."""
        yield StreamChunk(content="", provider="google", model=model, done=False)
