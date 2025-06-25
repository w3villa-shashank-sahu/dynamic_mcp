"""
Weather MCP Server
Provides weather and time information tools
"""

import json
import sys
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import importlib

# Add the parent directory to the path to import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.weather_tools import WEATHER_TOOLS


app = FastAPI(
    title="Weather MCP Server",
    description="MCP server providing weather and time information tools",
    version="1.0.0"
)

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend's URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ToolRequest(BaseModel):
    tool_name: str
    parameters: Optional[Dict[str, Any]] = None


class ToolResponse(BaseModel):
    success: bool
    data: Dict[str, Any]
    message: str


@app.get("/")
async def root():
    """Root endpoint with server information"""
    return {
        "name": "Weather MCP Server",
        "description": "Provides weather and time information tools",
        "version": "1.0.0",
        "tools": list(WEATHER_TOOLS.keys())
    }


@app.get("/tools")
async def list_tools():
    """List all available tools"""
    return {
        "tools": {
            name: {
                "description": tool["description"],
                "parameters": tool["parameters"]
            }
            for name, tool in WEATHER_TOOLS.items()
        }
    }


@app.post("/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute a tool with given parameters"""
    if request.tool_name not in WEATHER_TOOLS:
        raise HTTPException(
            status_code=400,
            detail=f"Tool '{request.tool_name}' not found. Available tools: {list(WEATHER_TOOLS.keys())}"
        )
    
    tool = WEATHER_TOOLS[request.tool_name]
    parameters = request.parameters or {}
    
    try:
        # Execute the tool function
        result = tool["function"](**parameters)
        return ToolResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error executing tool '{request.tool_name}': {str(e)}"
        )


@app.post("/reload_tools")
async def reload_tools():
    """
    Reload the WEATHER_TOOLS from tools.weather_tools.
    """
    global WEATHER_TOOLS
    try:
        import tools.weather_tools
        importlib.reload(tools.weather_tools)
        WEATHER_TOOLS = tools.weather_tools.WEATHER_TOOLS
        return {"success": True, "message": "WEATHER_TOOLS reloaded.", "tools": list(WEATHER_TOOLS.keys())}
    except Exception as e:
        return {"success": False, "message": f"Failed to reload: {str(e)}"}


if __name__ == "__main__":
    print("Starting Weather MCP Server on port 3001...")
    print("Available tools:", list(WEATHER_TOOLS.keys()))
    uvicorn.run(app, host="0.0.0.0", port=3001) 