"""
Main ADK Agent Application - Refactored to use LlmAgent pattern
Uses Google Gemini to intelligently select MCPs and tools based on user prompts
"""

import json
import os
import sys
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai
from datetime import datetime
import asyncio
import re

# Logger stub
class SimpleLogger:
    def info(self, msg): print(f"[INFO] {msg}")
    def debug(self, msg): print(f"[DEBUG] {msg}")
    def warning(self, msg): print(f"[WARNING] {msg}")
    def error(self, msg, exc_info=False): print(f"[ERROR] {msg}")

logger = SimpleLogger()

# Lifecycle hooks stubs
async def after_agent_invocation_callback_context(*args, **kwargs): pass
async def before_agent_invocation_callback_context(*args, **kwargs): pass
def simple_after_tool_modifier(*args, **kwargs): return args[0] if args else None
def simple_before_tool_modifier(*args, **kwargs): return args[0] if args else None

# LlmAgent stub
class LlmAgent:
    def __init__(self, name, model, instruction, description, output_key, tools, before_agent_callback, after_agent_callback, before_tool_callback, after_tool_callback):
        self.name = name
        self.model = model
        self.instruction = instruction
        self.description = description
        self.output_key = output_key
        self.tools = tools
        self.before_agent_callback = before_agent_callback
        self.after_agent_callback = after_agent_callback
        self.before_tool_callback = before_tool_callback
        self.after_tool_callback = after_tool_callback
        
    async def run(self, user_prompt):
        # This will be replaced by the actual ADK logic
        return await self.tools[0].execute_user_request(user_prompt)

# LLM engine stub
def get_llm_engine(name):
    return f"llm_engine_stub_for_{name}"

# Load environment variables
load_dotenv()

# Configure Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    print("Error: GOOGLE_API_KEY not found in environment variables")
    print("Please set your Google API key in the .env file")
    sys.exit(1)

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')


class MCPClient:
    """Client for interacting with MCP servers"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def list_tools(self) -> Dict[str, Any]:
        """Get list of available tools from MCP server"""
        try:
            response = requests.get(f"{self.base_url}/tools")
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error connecting to MCP server at {self.base_url}: {e}")
            return {"tools": {}}
    
    def execute_tool(self, tool_name: str, parameters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a tool on the MCP server"""
        try:
            payload = {
                "tool_name": tool_name,
                "parameters": parameters or {}
            }
            response = requests.post(f"{self.base_url}/execute", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                "success": False,
                "message": f"Error executing tool: {e}",
                "data": {}
            }


class ADKAgentCore:
    """Core ADK Agent logic - your original implementation"""
    
    def __init__(self):
        self.mcp_servers = {
            "weather_mcp": {
                "name": "Weather MCP",
                "description": "Provides weather and time information",
                "url": "http://localhost:3001",
                "tools": ["getWeather", "getTime"]
            },
            "calculator_mcp": {
                "name": "Calculator MCP", 
                "description": "Provides basic mathematical operations",
                "url": "http://localhost:3002",
                "tools": ["addNumber", "subtractNumber"]
            }
        }
        
        self.mcp_clients = {
            name: MCPClient(server["url"])
            for name, server in self.mcp_servers.items()
        }
    
    def get_available_tools(self) -> Dict[str, Any]:
        """Get all available tools from all MCP servers"""
        all_tools = {}
        for mcp_name, client in self.mcp_clients.items():
            try:
                tools_response = client.list_tools()
                all_tools[mcp_name] = {
                    "server_info": self.mcp_servers[mcp_name],
                    "tools": tools_response.get("tools", {})
                }
            except Exception as e:
                print(f"Warning: Could not fetch tools from {mcp_name}: {e}")
        
        return all_tools
    
    def select_mcp_and_tool(self, user_prompt: str) -> tuple[Optional[str], Optional[str], Optional[Dict[str, Any]], str]:
        """Use Gemini to select the appropriate MCP and tool based on user prompt"""
        
        # Get available tools
        available_tools = self.get_available_tools()
        
        # Create a prompt for Gemini to analyze
        system_prompt = f"""
        You are an AI agent that needs to select the appropriate MCP (Model Context Protocol) server and tool based on a user's request.

        Available MCP servers and their tools:

        {json.dumps(available_tools, indent=2)}

        Your task is to:
        1. Analyze the user's request
        2. Select the most appropriate MCP server
        3. Select the most appropriate tool from that MCP
        4. Extract any relevant parameters from the user's request

        Respond with a JSON object in this exact format:
        {{
            "mcp_server": "server_name",
            "tool_name": "tool_name", 
            "parameters": {{"param1": "value1", "param2": "value2"}},
            "reasoning": "Brief explanation of why you chose this MCP and tool"
        }}

        If no appropriate MCP or tool is found, respond with:
        {{
            "mcp_server": null,
            "tool_name": null,
            "parameters": {{}},
            "reasoning": "Explanation of why no suitable MCP/tool was found"
        }}

        User request: {user_prompt}
        """

        try:
            response = model.generate_content(system_prompt)
            # Try to extract the text from the Gemini response
            try:
                response_text = response.candidates[0].content.parts[0].text
            except Exception:
                response_text = getattr(response, 'text', None) or str(response)

            # Remove Markdown code block if present
            if response_text.strip().startswith("```"):
                # Remove the first line (```json or ```)
                lines = response_text.strip().splitlines()
                # Remove the first and last line (the backticks)
                json_str = "\n".join(lines[1:-1])
            else:
                # Try to extract JSON from the response, even if it's surrounded by text/markdown
                match = re.search(r'({[\s\S]*})', response_text)
                if match:
                    json_str = match.group(1)
                else:
                    json_str = response_text  # fallback

            result = json.loads(json_str)
            return (
                result.get("mcp_server"),
                result.get("tool_name"), 
                result.get("parameters", {}),
                result.get("reasoning", "")
            )
        except Exception as e:
            print(f"Error in AI selection: {e}")
            return None, None, {}, "Error in AI processing"
    
    async def execute_user_request(self, user_prompt: str) -> Dict[str, Any]:
        """Execute a user request by selecting and using appropriate MCP tools"""
        
        print(f"\n🤖 Analyzing request: {user_prompt}")
        
        # Select MCP and tool using AI
        mcp_server, tool_name, parameters, reasoning = self.select_mcp_and_tool(user_prompt)
        
        print(f"🧠 AI Reasoning: {reasoning}")
        
        if not mcp_server or not tool_name:
            print("❌ No MCP found")
            return {
                "success": False,
                "message": "No MCP found",
                "data": {}
            }
        
        print(f"🔧 Selected MCP: {self.mcp_servers[mcp_server]['name']}")
        print(f"🛠️  Selected Tool: {tool_name}")
        if parameters:
            print(f"📝 Parameters: {parameters}")
        
        # Execute the tool
        try:
            client = self.mcp_clients[mcp_server]
            result = client.execute_tool(tool_name, parameters)
            
            if result.get("success"):
                print(f"✅ Result: {result['message']}")
                return result
            else:
                print(f"❌ Error: {result.get('message', 'Unknown error')}")
                return result
                
        except Exception as e:
            error_msg = f"Error executing tool: {e}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "message": error_msg,
                "data": {}
            }


class ADKAgentWrapper:
    """Wrapper to integrate ADK Agent with LlmAgent pattern"""
    
    def __init__(self):
        self.adk_core = ADKAgentCore()
        self.agent = None
    
    async def initialize_agent(self) -> Optional[LlmAgent]:
        """Initialize the LlmAgent with ADK core functionality"""
        try:
            logger.info("Setting up ADK agent with LlmAgent pattern")
            adk_model = get_llm_engine('ADK_Universal_Agent')
            date = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
            
            # Get available tools info for the instruction
            available_tools = self.adk_core.get_available_tools()
            tools_info = []
            for mcp_name, mcp_data in available_tools.items():
                server_info = mcp_data["server_info"]
                tools_list = list(mcp_data["tools"].keys()) if mcp_data["tools"] else server_info["tools"]
                tools_info.append(f"• {server_info['name']}: {server_info['description']}")
                tools_info.append(f"  Available tools: {', '.join(tools_list)}")
            
            instruction = f"""
You are an intelligent ADK Agent that can interact with multiple MCP (Model Context Protocol) servers to help users with various tasks.

Current date and time: {date}

Available MCP servers and their capabilities:
{chr(10).join(tools_info)}

Your role is to:
1. Analyze user requests and understand their intent
2. Select and use the most appropriate tools from the available MCP servers
3. Provide helpful, accurate responses based on the tool results
4. Handle errors gracefully and suggest alternatives when needed

Guidelines:
- Always try to fulfill the user's request using the available tools
- If a request cannot be handled by available tools, respond with "No MCP found"
- Provide clear, concise responses
- When using tools, explain what you're doing and why
"""
            
            self.agent = LlmAgent(
                name="adk_universal_agent",
                model=adk_model,
                instruction=instruction,
                description="Universal ADK agent that intelligently selects and uses MCP servers based on user requests",
                output_key="adk_output",
                tools=[self.adk_core],  # Pass the core as a tool
                before_agent_callback=before_agent_invocation_callback_context,
                after_agent_callback=after_agent_invocation_callback_context,
                before_tool_callback=simple_before_tool_modifier,
                after_tool_callback=simple_after_tool_modifier
            )
            
            return self.agent
            
        except Exception as e:
            logger.error(f"Error in initialize_agent: {e}", exc_info=True)
            return None
    
    async def execute_request(self, user_prompt: str) -> Dict[str, Any]:
        """Execute a user request"""
        try:
            if not self.agent:
                return {
                    "success": False,
                    "message": "Agent not initialized",
                    "data": {}
                }
            
            logger.info(f"🤖 Executing request: {user_prompt}")
            
            # Execute using the agent (which internally uses ADK core logic)
            result = await self.agent.run(user_prompt)
            
            logger.info(f"✅ Agent execution completed")
            return {
                "success": True,
                "message": "Request executed successfully",
                "data": result
            }
            
        except Exception as e:
            error_msg = f"Error executing request: {e}"
            logger.error(error_msg, exc_info=True)
            return {
                "success": False,
                "message": error_msg,
                "data": {}
            }
    
    async def run_interactive(self):
        """Run the agent in interactive mode"""
        print("🚀 ADK Agent with MCP Integration (LlmAgent Pattern)")
        print("=" * 60)
        
        # Initialize agent
        agent = await self.initialize_agent()
        
        if not agent:
            print("❌ Agent could not be initialized.")
            return
        
        # Check MCP server connections
        print("🔍 Checking MCP server connections...")
        for name, client in self.adk_core.mcp_clients.items():
            try:
                response = requests.get(f"{client.base_url}/", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {name}: Connected")
                else:
                    print(f"⚠️  {name}: Unexpected status {response.status_code}")
            except requests.RequestException:
                print(f"❌ {name}: Not connected (make sure to start the MCP server)")
        
        print("\nAvailable MCPs:")
        for name, server in self.adk_core.mcp_servers.items():
            print(f"  • {server['name']}: {server['description']}")
            print(f"    Tools: {', '.join(server['tools'])}")
        
        print("=" * 60)
        print("Enter your requests (type 'quit' to exit):")
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not user_input:
                    continue
                
                # Execute the request
                result = await self.execute_request(user_input)
                
                # Display result
                if result.get("success"):
                    print(f"\n📊 Response: {result['data']}")
                else:
                    print(f"\n❌ Failed: {result.get('message', 'Unknown error')}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")


async def main():
    """Main function"""
    print("🔧 Initializing ADK Agent...")
    
    agent_wrapper = ADKAgentWrapper()
    
    # Run interactive mode
    await agent_wrapper.run_interactive()


if __name__ == "__main__":
    asyncio.run(main())