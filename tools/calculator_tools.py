"""
Calculator MCP Tools Implementation
Contains addNumber and subtractNumber tools
"""

import json
from typing import Dict, Any


def add_number(a: float, b: float) -> Dict[str, Any]:
    """
    Add two numbers together
    
    Args:
        a: First number to add
        b: Second number to add
        
    Returns:
        Dictionary containing the result
    """
    result = a + b
    
    return {
        "success": True,
        "data": {
            "operation": "addition",
            "a": a,
            "b": b,
            "result": result,
            "formula": f"{a} + {b} = {result}"
        },
        "message": f"Added {a} and {b} to get {result}"
    }


def subtract_number(a: float, b: float) -> Dict[str, Any]:
    """
    Subtract the second number from the first
    
    Args:
        a: Number to subtract from
        b: Number to subtract
        
    Returns:
        Dictionary containing the result
    """
    result = a - b
    
    return {
        "success": True,
        "data": {
            "operation": "subtraction",
            "a": a,
            "b": b,
            "result": result,
            "formula": f"{a} - {b} = {result}"
        },
        "message": f"Subtracted {b} from {a} to get {result}"
    }


# Tool registry for MCP server
CALCULATOR_TOOLS = {
            "function": add_number,
        "description": "Add two numbers together",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "First number to add"
                },
                "b": {
                    "type": "number",
                    "description": "Second number to add"
                }
            },
            "required": ["a", "b"]
        }
    },
    "subtractNumber": {
        "function": subtract_number,
        "description": "Subtract the second number from the first",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {
                    "type": "number",
                    "description": "Number to subtract from"
                },
                "b": {
                    "type": "number",
                    "description": "Number to subtract"
                }
            },
            "required": ["a", "b"]
        }
    }
} 