"""
Calculator MCP Server
Provides basic mathematical operations tools
"""

import json
import sys
import os
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

# Add the parent directory to the path to import tools
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tools.calculator_tools import CALCULATOR_TOOLS, add_number, subtract_number


app = FastAPI(
    title="Calculator MCP Server",
    description="MCP server providing basic mathematical operations tools",
    version="1.0.0"
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
        "name": "Calculator MCP Server",
        "description": "Provides basic mathematical operations tools",
        "version": "1.0.0",
        "tools": list(CALCULATOR_TOOLS.keys())
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
            for name, tool in CALCULATOR_TOOLS.items()
        }
    }


@app.post("/execute", response_model=ToolResponse)
async def execute_tool(request: ToolRequest):
    """Execute a tool with given parameters"""
    if request.tool_name not in CALCULATOR_TOOLS:
        raise HTTPException(
            status_code=400,
            detail=f"Tool '{request.tool_name}' not found. Available tools: {list(CALCULATOR_TOOLS.keys())}"
        )
    
    tool = CALCULATOR_TOOLS[request.tool_name]
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


# @app.get("/tools/{tool_name}")
# async def get_tool_info(tool_name: str):
#     """Get information about a specific tool"""
#     if tool_name not in CALCULATOR_TOOLS:
#         raise HTTPException(
#             status_code=404,
#             detail=f"Tool '{tool_name}' not found"
#         )
    
#     return {
#         "name": tool_name,
#         "description": CALCULATOR_TOOLS[tool_name]["description"],
#         "parameters": CALCULATOR_TOOLS[tool_name]["parameters"]
#     }


if __name__ == "__main__":
    print("Starting Calculator MCP Server on port 3002...")
    print("Available tools:", list(CALCULATOR_TOOLS.keys()))
    uvicorn.run(app, host="0.0.0.0", port=3002) 