"""MCP client for tool integration."""

from typing import Dict, Any, List, Optional, Callable
import asyncio
import logging
import json
import time

from mcp.protocols.transport import (
    MCPTransport, StdIOTransport, HTTPTransport, WebSocketTransport
)
from mcp.protocols.schema import MCPProtocol

logger = logging.getLogger(__name__)


class MCPConnection:
    """Represents a connection to an MCP server."""
    
    def __init__(self, server_name: str, transport: MCPTransport):
        """Initialize MCP connection.
        
        Args:
            server_name: Name of the server.
            transport: Transport instance.
        """
        self.server_name = server_name
        self.transport = transport
        self.tools = {}
        self.resources = {}
        self.capabilities = {}
        self.initialized = False
        self.last_heartbeat = time.time()
    
    async def initialize(self) -> bool:
        """Initialize the MCP connection.
        
        Returns:
            True if successful.
        """
        try:
            # Connect transport
            if not await self.transport.connect():
                return False
            
            # Send initialize request
            init_request = MCPProtocol.create_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {}
                },
                "clientInfo": {
                    "name": "prompt-engineering-system",
                    "version": "1.0.0"
                }
            })
            
            await self.transport.send(init_request)
            
            # Wait for response
            response = await self.transport.receive()
            
            if response.get("type") == "response":
                self.initialized = True
                logger.info(f"MCP connection initialized: {self.server_name}")
                
                # Get tools and resources
                await self._discover_capabilities()
                return True
            else:
                logger.error(f"Failed to initialize MCP connection: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing MCP connection: {e}")
            return False
    
    async def _discover_capabilities(self) -> None:
        """Discover server capabilities."""
        try:
            # List tools
            tools_request = MCPProtocol.create_request("tools/list")
            await self.transport.send(tools_request)
            
            tools_response = await self.transport.receive()
            if tools_response.get("type") == "response":
                tools = tools_response.get("result", {}).get("tools", [])
                for tool in tools:
                    self.tools[tool["name"]] = tool
                
                logger.info(f"Discovered {len(self.tools)} tools on {self.server_name}")
            
            # List resources
            resources_request = MCPProtocol.create_request("resources/list")
            await self.transport.send(resources_request)
            
            resources_response = await self.transport.receive()
            if resources_response.get("type") == "response":
                resources = resources_response.get("result", {}).get("resources", [])
                for resource in resources:
                    self.resources[resource["uri"]] = resource
                
                logger.info(f"Discovered {len(self.resources)} resources on {self.server_name}")
                
        except Exception as e:
            logger.error(f"Error discovering capabilities: {e}")
    
    async def execute_tool(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Execute a tool on the connected server.
        
        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.
            
        Returns:
            Tool execution result.
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Connection not initialized"
            }
        
        if tool_name not in self.tools:
            return {
                "success": False,
                "error": f"Tool '{tool_name}' not found"
            }
        
        try:
            tool_request = MCPProtocol.create_request("tools/call", {
                "name": tool_name,
                "arguments": arguments
            })
            
            await self.transport.send(tool_request)
            
            # Wait for response
            response = await self.transport.receive()
            
            if response.get("type") == "response":
                result = response.get("result", {})
                return {
                    "success": True,
                    "result": result,
                    "tool": tool_name,
                    "arguments": arguments
                }
            else:
                error = response.get("error", "Unknown error")
                return {
                    "success": False,
                    "error": error,
                    "tool": tool_name
                }
                
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }
    
    async def read_resource(self, resource_uri: str) -> Dict[str, Any]:
        """Read a resource from the connected server.
        
        Args:
            resource_uri: URI of the resource to read.
            
        Returns:
            Resource content.
        """
        if not self.initialized:
            return {
                "success": False,
                "error": "Connection not initialized"
            }
        
        if resource_uri not in self.resources:
            return {
                "success": False,
                "error": f"Resource '{resource_uri}' not found"
            }
        
        try:
            resource_request = MCPProtocol.create_request("resources/read", {
                "uri": resource_uri
            })
            
            await self.transport.send(resource_request)
            
            # Wait for response
            response = await self.transport.receive()
            
            if response.get("type") == "response":
                result = response.get("result", {})
                return {
                    "success": True,
                    "content": result.get("contents", ""),
                    "uri": resource_uri
                }
            else:
                error = response.get("error", "Unknown error")
                return {
                    "success": False,
                    "error": error,
                    "uri": resource_uri
                }
                
        except Exception as e:
            logger.error(f"Error reading resource {resource_uri}: {e}")
            return {
                "success": False,
                "error": str(e),
                "uri": resource_uri
            }
    
    async def disconnect(self) -> None:
        """Disconnect from the server."""
        try:
            await self.transport.disconnect()
            self.initialized = False
            logger.info(f"Disconnected from {self.server_name}")
        except Exception as e:
            logger.error(f"Error disconnecting from {self.server_name}: {e}")
    
    def get_tool_info(self, tool_name: str) -> Dict[str, Any]:
        """Get information about a tool.
        
        Args:
            tool_name: Name of the tool.
            
        Returns:
            Tool information.
        """
        return self.tools.get(tool_name, {})
    
    def list_available_tools(self) -> List[str]:
        """List all available tools.
        
        Returns:
            List of tool names.
        """
        return list(self.tools.keys())
    
    def list_available_resources(self) -> List[str]:
        """List all available resources.
        
        Returns:
            List of resource URIs.
        """
        return list(self.resources.keys())


class MCPClient:
    """Model Context Protocol client with server management."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """Initialize MCP client.
        
        Args:
            config: Client configuration.
        """
        self.config = config or {}
        self.connections = {}
        self.default_timeout = self.config.get("timeout", 30)
        self.max_retries = self.config.get("max_retries", 3)
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the MCP client.
        
        Returns:
            True if successful.
        """
        server_configs = self.config.get("servers", {})
        
        for server_name, server_config in server_configs.items():
            if not server_config.get("enabled", False):
                continue
            
            try:
                connection = await self._create_connection(server_name, server_config)
                if connection:
                    if await connection.initialize():
                        self.connections[server_name] = connection
                    else:
                        logger.warning(f"Failed to initialize connection to {server_name}")
                        
            except Exception as e:
                logger.error(f"Failed to create connection to {server_name}: {e}")
        
        self._initialized = True
        logger.info(f"MCP client initialized with {len(self.connections)} connections")
        return len(self.connections) > 0
    
    async def _create_connection(self, server_name: str, server_config: Dict[str, Any]) -> Optional[MCPConnection]:
        """Create a connection to a server.
        
        Args:
            server_name: Name of the server.
            server_config: Server configuration.
            
        Returns:
            Connection instance or None.
        """
        transport_type = server_config.get("transport", "stdio")
        transport_config = server_config.get("transport_config", {})
        
        if transport_type == "stdio":
            transport = StdIOTransport(transport_config)
        elif transport_type == "http":
            transport = HTTPTransport(transport_config)
        elif transport_type == "websocket":
            transport = WebSocketTransport(transport_config)
        else:
            logger.error(f"Unknown transport type: {transport_type}")
            return None
        
        return MCPConnection(server_name, transport)
    
    async def execute_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any] = None,
        server_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a tool on a server.
        
        Args:
            tool_name: Name of the tool to execute.
            arguments: Tool arguments.
            server_name: Specific server to use (optional).
            
        Returns:
            Tool execution result.
        """
        if not self._initialized:
            await self.initialize()
        
        arguments = arguments or {}
        
        # If server specified, use only that server
        if server_name:
            if server_name in self.connections:
                return await self.connections[server_name].execute_tool(tool_name, arguments)
            else:
                return {
                    "success": False,
                    "error": f"Server '{server_name}' not connected"
                }
        
        # Search for tool across all connected servers
        for name, connection in self.connections.items():
            if tool_name in connection.tools:
                logger.info(f"Executing tool '{tool_name}' on server '{name}'")
                return await connection.execute_tool(tool_name, arguments)
        
        return {
            "success": False,
            "error": f"Tool '{tool_name}' not found on any connected server"
        }
    
    async def read_resource(
        self,
        resource_uri: str,
        server_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Read a resource from a server.
        
        Args:
            resource_uri: URI of the resource to read.
            server_name: Specific server to use (optional).
            
        Returns:
            Resource content.
        """
        if not self._initialized:
            await self.initialize()
        
        # If server specified, use only that server
        if server_name:
            if server_name in self.connections:
                return await self.connections[server_name].read_resource(resource_uri)
            else:
                return {
                    "success": False,
                    "error": f"Server '{server_name}' not connected"
                }
        
        # Search for resource across all connected servers
        for name, connection in self.connections.items():
            if resource_uri in connection.resources:
                logger.info(f"Reading resource '{resource_uri}' from server '{name}'")
                return await connection.read_resource(resource_uri)
        
        return {
            "success": False,
            "error": f"Resource '{resource_uri}' not found on any connected server"
        }
    
    def list_all_tools(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all available tools across all servers.
        
        Returns:
            Dictionary mapping server names to tool lists.
        """
        result = {}
        for server_name, connection in self.connections.items():
            tools = [connection.get_tool_info(tool_name) for tool_name in connection.list_available_tools()]
            result[server_name] = tools
        
        return result
    
    def list_all_resources(self) -> Dict[str, List[Dict[str, Any]]]:
        """List all available resources across all servers.
        
        Returns:
            Dictionary mapping server names to resource lists.
        """
        result = {}
        for server_name, connection in self.connections.items():
            resources = [
                connection.resources.get(uri, {})
                for uri in connection.list_available_resources()
            ]
            result[server_name] = resources
        
        return result
    
    def get_connection_info(self) -> Dict[str, Any]:
        """Get information about all connections.
        
        Returns:
            Connection information.
        """
        return {
            "total_connections": len(self.connections),
            "total_tools": sum(len(conn.tools) for conn in self.connections.values()),
            "total_resources": sum(len(conn.resources) for conn in self.connections.values()),
            "servers": {
                name: {
                    "initialized": conn.initialized,
                    "tool_count": len(conn.tools),
                    "resource_count": len(conn.resources),
                    "transport": conn.transport.__class__.__name__
                }
                for name, conn in self.connections.items()
            }
        }
    
    async def disconnect_all(self) -> None:
        """Disconnect from all servers."""
        for server_name, connection in self.connections.items():
            logger.info(f"Disconnecting from {server_name}")
            await connection.disconnect()
        
        self.connections.clear()
        self._initialized = False
        logger.info("Disconnected from all MCP servers")
    
    async def reconnect_server(self, server_name: str) -> bool:
        """Reconnect to a specific server.
        
        Args:
            server_name: Name of the server to reconnect.
            
        Returns:
            True if successful.
        """
        if server_name in self.connections:
            await self.connections[server_name].disconnect()
            del self.connections[server_name]
        
        server_configs = self.config.get("servers", {})
        if server_name in server_configs:
            try:
                connection = await self._create_connection(server_name, server_configs[server_name])
                if connection and await connection.initialize():
                    self.connections[server_name] = connection
                    logger.info(f"Successfully reconnected to {server_name}")
                    return True
            except Exception as e:
                logger.error(f"Failed to reconnect to {server_name}: {e}")
        
        return False
