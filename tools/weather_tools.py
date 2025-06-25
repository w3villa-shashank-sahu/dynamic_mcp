# Weather MCP Tools Implementation
# Contains getWeather and getTime tools with dummy data


import json
import sys
import os
import inspect

# Add the parent directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

namespace = {}
from backend.weather_backend import get_weather_data, get_tools_config

# Load the function definitions from functionStore.txt and execute them in the namespace
code_str = get_weather_data()
if(code_str['status'] == 'success'):
    exec(code_str['data'], namespace)
    print("Namespace after loading functions:", list(namespace.keys()))
    functions = {k: v for k, v in namespace.items() if inspect.isfunction(v)}
    print("Functions found:", list(functions.keys()))
else:
    raise RuntimeError(f"Failed to load weather functions: {code_str['message']}")

# # Dynamically extract all functions from the namespace
def get_tool_template(func):
    sig = inspect.signature(func)
    params = {
        "type": "object",
        "properties": {
            name: {
                "type": "string",  # You can improve this by inspecting type hints
                "description": f"Parameter {name}"
            }
            for name in sig.parameters
        }
    }
    return {
        "function": func,
        "description": func.__doc__ or f"Auto-generated tool for {func.__name__}",
        "parameters": params
    }

WEATHER_TOOLS = {name: get_tool_template(func) for name, func in functions.items()}