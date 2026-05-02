# tools/tool_registry.py

from typing import Dict, Any, Optional, Callable
from pydantic import BaseModel
import json

class ToolSchema(BaseModel):
    name: str
    description: str
    parameters: Dict[str, Any]
    function: Optional[Callable] = None
    fallbacks: list[str] = []
    
    class Config:
        arbitrary_types_allowed = True

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolSchema] = {}
    
    def register(self, tool: ToolSchema):
        """Register a tool dynamically — no code changes needed"""
        self._tools[tool.name] = tool
        print(f"[Registry] Tool registered: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[ToolSchema]:
        return self._tools.get(name)
    
    def get_all_tools(self) -> Dict[str, ToolSchema]:
        return self._tools
    
    def get_tools_for_llm(self) -> list[Dict]:
        """Returns tool definitions in OpenAI function calling format"""
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.parameters
            }
            for tool in self._tools.values()
        ]
    
    def execute(self, tool_name: str, 
                params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool with fallback chain support"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {"error": f"Tool {tool_name} not found"}
        
        try:
            if tool.function:
                result = tool.function(**params)
                return {"success": True, "data": result, 
                        "source": tool_name}
        except Exception as e:
            print(f"[Registry] {tool_name} failed: {e}")
            # Try fallbacks
            for fallback_name in tool.fallbacks:
                try:
                    fallback = self.get_tool(fallback_name)
                    if fallback and fallback.function:
                        result = fallback.function(**params)
                        return {
                            "success": True, 
                            "data": result,
                            "source": fallback_name,
                            "fallback_used": True,
                            "original_tool": tool_name
                        }
                except Exception as fe:
                    print(f"[Registry] Fallback {fallback_name} failed: {fe}")
                    continue
            
            return {
                "success": False, 
                "error": str(e),
                "tool": tool_name
            }
    
    def list_tools(self) -> list[str]:
        return list(self._tools.keys())

# Global registry instance
registry = ToolRegistry()