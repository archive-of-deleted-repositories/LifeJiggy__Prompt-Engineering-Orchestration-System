"""MCP transport layer with stdio and HTTP implementations."""

from typing import Dict, Any, List, Optional, Callable, AsyncIterator
import asyncio
import json
import logging
import uuid
from abc import ABC, abstractmethod

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import websockets
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

logger = logging.getLogger(__name__)


class MCPTransport(ABC):
    """Abstract transport layer for MCP communication."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize the transport.
        
        Args:
            config: Transport configuration.
        """
        self.config = config or {}
        self._handlers = {}
        self._connected = False
        self._message_queue = asyncio.Queue()
        self._running = False
    
    @abstractmethod
    async def connect(self) -> bool:
        """Establish connection.
        
        Returns:
            True if successful.
        """
        pass
    
    @abstractmethod
    async def disconnect(self) -> None:
        """Close connection."""
        pass
    
    @abstractmethod
    async def send(self, message: Dict[str, Any]) -> None:
        """Send a message.
        
        Args:
            message: Message to send.
        """
        pass
    
    async def receive(self) -> Dict[str, Any]:
        """Receive a message.
        
        Returns:
            Received message.
        """
        try:
            return await asyncio.wait_for(self._message_queue.get(), timeout=1.0)
        except asyncio.TimeoutError:
            return {}
    
    def register_handler(
        self,
        message_type: str,
        handler: Callable
    ) -> None:
        """Register a message handler.
        
        Args:
            message_type: Message type.
            handler: Handler function.
        """
        self._handlers[message_type] = handler
    
    async def handle_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an incoming message.
        
        Args:
            message: Incoming message.
            
        Returns:
            Response message.
        """
        msg_type = message.get("type", "unknown")
        handler = self._handlers.get(msg_type)
        
        if handler:
            try:
                return await handler(message)
            except Exception as e:
                logger.error(f"Error handling message {msg_type}: {e}")
                return MCPProtocol.create_error(
                    message.get("id", "unknown"),
                    f"Handler error: {str(e)}",
                    code=-2
                )
        
        return MCPProtocol.create_error(
            message.get("id", "unknown"),
            f"No handler for {msg_type}",
            code=-3
        )


class StdIOTransport(MCPTransport):
    """Standard I/O transport for MCP."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize stdio transport.
        
        Args:
            config: Transport configuration.
        """
        super().__init__(config)
        self._process = None
        self._stdio_task = None
        self.command = self.config.get("command", [])
    
    async def connect(self) -> bool:
        """Connect to subprocess via stdio."""
        try:
            if not self.command:
                logger.error("No command specified for stdio transport")
                return False
            
            logger.info(f"Starting subprocess: {' '.join(self.command)}")
            self._process = await asyncio.create_subprocess_exec(
                *self.command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            self._connected = True
            self._running = True
            self._stdio_task = asyncio.create_task(self._read_stdio())
            
            logger.info("StdIO transport connected")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect stdio transport: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from subprocess."""
        self._running = False
        
        if self._stdio_task:
            self._stdio_task.cancel()
            try:
                await self._stdio_task
            except asyncio.CancelledError:
                pass
        
        if self._process:
            self._process.terminate()
            try:
                await self._process.wait()
            except asyncio.TimeoutError:
                self._process.kill()
                await self._process.wait()
        
        self._connected = False
        logger.info("StdIO transport disconnected")
    
    async def send(self, message: Dict[str, Any]) -> None:
        """Send message to subprocess stdin."""
        if not self._process or not self._connected:
            return
        
        try:
            message_json = json.dumps(message) + "\n"
            data = message_json.encode('utf-8')
            self._process.stdin.write(data)
            await self._process.stdin.drain()
        except Exception as e:
            logger.error(f"Failed to send message via stdio: {e}")
    
    async def _read_stdio(self) -> None:
        """Read messages from subprocess stdout."""
        if not self._process:
            return
        
        buffer = ""
        
        while self._running:
            try:
                line = await self._process.stdout.readline()
                if not line:
                    break
                
                line = line.decode('utf-8').strip()
                if not line:
                    continue
                
                buffer += line
                
                # Try to parse complete JSON objects
                while buffer:
                    try:
                        message = json.loads(buffer)
                        await self._message_queue.put(message)
                        buffer = ""
                        break
                    except json.JSONDecodeError:
                        # Incomplete JSON, wait for more data
                        if len(buffer) > 10000:  # Prevent buffer overflow
                            logger.warning("StdIO buffer too large, resetting")
                            buffer = ""
                        break
                
            except Exception as e:
                logger.error(f"Error reading from stdio: {e}")
                break
    
    async def stream(self) -> AsyncIterator[Dict[str, Any]]:
        """Stream messages from subprocess.
        
        Yields:
            Messages from subprocess.
        """
        while self._connected:
            try:
                message = await self.receive()
                if message:
                    yield message
            except Exception as e:
                logger.error(f"Error in stdio stream: {e}")
                break


class HTTPTransport(MCPTransport):
    """HTTP transport for MCP."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize HTTP transport.
        
        Args:
            config: Transport configuration.
        """
        super().__init__(config)
        self.session = None
        self.base_url = self.config.get("base_url", "http://localhost:3000")
        self.headers = self.config.get("headers", {})
        self.timeout = self.config.get("timeout", 30)
        self._message_id = 0
    
    async def connect(self) -> bool:
        """Connect to HTTP endpoint."""
        try:
            if not AIOHTTP_AVAILABLE:
                logger.error("aiohttp not available for HTTP transport")
                return False
            
            self.session = aiohttp.ClientSession(
                headers=self.headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
            
            # Test connection
            async with self.session.get(f"{self.base_url}/health") as response:
                if response.status == 200:
                    self._connected = True
                    logger.info(f"HTTP transport connected to {self.base_url}")
                    return True
                else:
                    logger.error(f"HTTP health check failed: {response.status}")
                    return False
                    
        except Exception as e:
            logger.error(f"Failed to connect HTTP transport: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close HTTP session."""
        if self.session:
            await self.session.close()
        self._connected = False
        logger.info("HTTP transport disconnected")
    
    async def send(self, message: Dict[str, Any]) -> None:
        """Send message via HTTP POST."""
        if not self.session or not self._connected:
            return
        
        try:
            self._message_id += 1
            message["id"] = str(self._message_id)
            
            async with self.session.post(
                f"{self.base_url}/mcp",
                json=message
            ) as response:
                if response.status == 200:
                    # Put response in queue for receive()
                    response_data = await response.json()
                    await self._message_queue.put(response_data)
                else:
                    logger.error(f"HTTP POST failed: {response.status}")
                    
        except Exception as e:
            logger.error(f"Failed to send message via HTTP: {e}")


class WebSocketTransport(MCPTransport):
    """WebSocket transport for MCP."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize WebSocket transport.
        
        Args:
            config: Transport configuration.
        """
        super().__init__(config)
        self.websocket = None
        self.url = self.config.get("url", "ws://localhost:3001/mcp")
        self._message_id = 0
    
    async def connect(self) -> bool:
        """Connect to WebSocket endpoint."""
        try:
            if not WEBSOCKETS_AVAILABLE:
                logger.error("websockets not available for WebSocket transport")
                return False
            
            self.websocket = await websockets.connect(self.url)
            self._connected = True
            
            # Start message reader task
            asyncio.create_task(self._read_websocket())
            
            logger.info(f"WebSocket transport connected to {self.url}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect WebSocket transport: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Close WebSocket connection."""
        self._connected = False
        if self.websocket:
            await self.websocket.close()
        logger.info("WebSocket transport disconnected")
    
    async def send(self, message: Dict[str, Any]) -> None:
        """Send message via WebSocket."""
        if not self.websocket or not self._connected:
            return
        
        try:
            self._message_id += 1
            message["id"] = str(self._message_id)
            message_json = json.dumps(message)
            await self.websocket.send(message_json)
        except Exception as e:
            logger.error(f"Failed to send message via WebSocket: {e}")
    
    async def _read_websocket(self) -> None:
        """Read messages from WebSocket."""
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    await self._message_queue.put(data)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON from WebSocket: {e}")
        except Exception as e:
            logger.error(f"Error reading WebSocket: {e}")
    
    async def stream(self) -> AsyncIterator[Dict[str, Any]]:
        """Stream messages from WebSocket.
        
        Yields:
            Messages from WebSocket.
        """
        while self._connected:
            try:
                message = await self.receive()
                if message:
                    yield message
            except Exception as e:
                logger.error(f"Error in WebSocket stream: {e}")
                break


class MCPProtocol:
    """MCP protocol message definitions."""
    
    MESSAGE_TYPES = {
        "request": "request",
        "response": "response",
        "notification": "notification",
        "error": "error"
    }
    
    REQUEST_TYPES = {
        "initialize": "initialize",
        "tools/list": "tools/list",
        "tools/call": "tools/call",
        "resources/list": "resources/list",
        "resources/read": "resources/read"
    }
    
    @staticmethod
    def create_request(
        request_type: str,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a request message.
        
        Args:
            request_type: Type of request.
            params: Request parameters.
            
        Returns:
            Request message.
        """
        return {
            "type": "request",
            "request_type": request_type,
            "params": params or {},
            "id": f"req_{str(uuid.uuid4())[:8]}"
        }
    
    @staticmethod
    def create_response(
        request_id: str,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create a response message.
        
        Args:
            request_id: Original request ID.
            result: Result data.
            
        Returns:
            Response message.
        """
        return {
            "type": "response",
            "request_id": request_id,
            "result": result
        }
    
    @staticmethod
    def create_notification(
        notification_type: str,
        data: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a notification message.
        
        Args:
            notification_type: Type of notification.
            data: Notification data.
            
        Returns:
            Notification message.
        """
        return {
            "type": "notification",
            "notification_type": notification_type,
            "data": data or {}
        }
    
    @staticmethod
    def create_error(
        request_id: str,
        error: str,
        code: int = -1
    ) -> Dict[str, Any]:
        """Create an error message.
        
        Args:
            request_id: Original request ID.
            error: Error message.
            error_code: Error code.
            
        Returns:
            Error message.
        """
        return {
            "type": "error",
            "request_id": request_id,
            "error": error,
            "code": code
        }
