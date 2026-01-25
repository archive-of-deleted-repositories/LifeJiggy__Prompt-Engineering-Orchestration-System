"""Filesystem MCP server."""

from typing import Dict, Any, List, Optional
import os
import json
from pathlib import Path


class FilesystemMCPServer:
    """MCP server for filesystem operations."""
    
    def __init__(self, root_path: str = "./data"):
        """Initialize the filesystem server.
        
        Args:
            root_path: Root directory for file operations.
        """
        self.root_path = Path(root_path)
        self.root_path.mkdir(parents=True, exist_ok=True)
        self._allowed_paths = set()
    
    def configure(self, config: Dict[str, Any]) -> None:
        """Configure the server.
        
        Args:
            config: Server configuration.
        """
        if "allowed_paths" in config:
            self._allowed_paths = set(config["allowed_paths"])
    
    def _resolve_path(self, filepath: str) -> Path:
        """Resolve and validate filepath.
        
        Args:
            filepath: User-provided filepath.
            
        Returns:
            Resolved Path object.
        """
        path = Path(filepath)
        
        if not path.is_absolute():
            path = self.root_path / path
        
        path = path.resolve()
        
        if self._allowed_paths:
            in_allowed = any(str(path).startswith(str(allowed)) for allowed in self._allowed_paths)
            if not in_allowed:
                raise PermissionError(f"Path not in allowed list: {filepath}")
        
        if not str(path).startswith(str(self.root_path.resolve())):
            raise PermissionError(f"Path outside root: {filepath}")
        
        return path
    
    def read_file(self, filepath: str) -> Dict[str, Any]:
        """Read a file.
        
        Args:
            filepath: Path to file.
            
        Returns:
            File content.
        """
        path = self._resolve_path(filepath)
        
        if not path.exists():
            return {"error": "File not found", "path": str(path)}
        
        if not path.is_file():
            return {"error": "Not a file", "path": str(path)}
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "content": content,
                "path": str(path),
                "size": len(content),
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "path": str(path)}
    
    def write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """Write to a file.
        
        Args:
            filepath: Path to file.
            content: Content to write.
            
        Returns:
            Write result.
        """
        path = self._resolve_path(filepath)
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "path": str(path),
                "size": len(content),
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "path": str(path)}
    
    def list_directory(self, directory: str) -> Dict[str, Any]:
        """List directory contents.
        
        Args:
            directory: Path to directory.
            
        Returns:
            Directory contents.
        """
        path = self._resolve_path(directory)
        
        if not path.exists():
            return {"error": "Directory not found", "path": str(path)}
        
        if not path.is_dir():
            return {"error": "Not a directory", "path": str(path)}
        
        try:
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "path": str(item)
                })
            
            return {
                "path": str(path),
                "items": items,
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "path": str(path)}
    
    def create_directory(self, directory: str) -> Dict[str, Any]:
        """Create a directory.
        
        Args:
            directory: Path to create.
            
        Returns:
            Create result.
        """
        path = self._resolve_path(directory)
        
        try:
            path.mkdir(parents=True, exist_ok=True)
            return {"path": str(path), "success": True}
        except Exception as e:
            return {"error": str(e), "path": str(path)}
    
    def delete_path(self, filepath: str) -> Dict[str, Any]:
        """Delete a file or directory.
        
        Args:
            filepath: Path to delete.
            
        Returns:
            Delete result.
        """
        path = self._resolve_path(filepath)
        
        try:
            if path.is_file():
                path.unlink()
            else:
                import shutil
                shutil.rmtree(path)
            
            return {"path": str(path), "success": True}
        except Exception as e:
            return {"error": str(e), "path": str(path)}
    
    def search_files(self, pattern: str, directory: str = ".") -> Dict[str, Any]:
        """Search for files matching pattern.
        
        Args:
            pattern: Glob pattern.
            directory: Search directory.
            
        Returns:
            Matching files.
        """
        path = self._resolve_path(directory)
        
        try:
            matches = list(path.rglob(pattern))
            
            results = []
            for match in matches[:100]:
                if match.is_file():
                    results.append(str(match))
            
            return {
                "directory": str(path),
                "pattern": pattern,
                "matches": results,
                "count": len(results),
                "success": True
            }
        except Exception as e:
            return {"error": str(e), "directory": str(path)}
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get available tools.
        
        Returns:
            List of tool definitions.
        """
        return [
            {
                "name": "read_file",
                "description": "Read the contents of a file",
                "parameters": {
                    "filepath": {"type": "string", "description": "Path to file"}
                }
            },
            {
                "name": "write_file",
                "description": "Write content to a file",
                "parameters": {
                    "filepath": {"type": "string", "description": "Path to file"},
                    "content": {"type": "string", "description": "Content to write"}
                }
            },
            {
                "name": "list_directory",
                "description": "List contents of a directory",
                "parameters": {
                    "directory": {"type": "string", "description": "Path to directory"}
                }
            },
            {
                "name": "create_directory",
                "description": "Create a new directory",
                "parameters": {
                    "directory": {"type": "string", "description": "Path to create"}
                }
            },
            {
                "name": "delete_path",
                "description": "Delete a file or directory",
                "parameters": {
                    "filepath": {"type": "string", "description": "Path to delete"}
                }
            },
            {
                "name": "search_files",
                "description": "Search for files matching a pattern",
                "parameters": {
                    "pattern": {"type": "string", "description": "Glob pattern"},
                    "directory": {"type": "string", "description": "Search directory"}
                }
            }
        ]
