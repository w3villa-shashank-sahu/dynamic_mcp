"""
Main ADK Agent Application
Uses Google Gemini to intelligently select MCPs and tools based on user prompts
"""

import json
import os
import sys
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv
import google.generativeai as genai
import re

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


class ADKAgent:
    """ADK Agent that uses Google Gemini to select MCPs and tools"""
    
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
            # name: weather_mcp
            # server: {"name": "Weather MCP", "description": "Provides weather and time information", "url": "http://localhost:3001", "tools": ["getWeather", "getTime"]}
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
    
    def select_mcp_and_tool(self, user_prompt: str) -> tuple[Optional[str], Optional[str], Optional[Dict[str, Any]]]:
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
    
    def execute_request(self, user_prompt: str) -> Dict[str, Any]:
        """Execute a user request by selecting and using appropriate MCP tools"""
        
        print(f"\n🤖 Analyzing request: {user_prompt}")
        
        # Select MCP and tool using AI
        mcp_server, tool_name, parameters, reasoning = self.select_mcp_and_tool(user_prompt)
        
        print(f"🧠 AI Reasoning: {reasoning}")
        
        if not mcp_server or not tool_name:
            return {
                "success": False,
                "message": "No appropriate MCP or tool found for this request",
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
    
    def run_interactive(self):
        """Run the agent in interactive mode"""
        print("🚀 ADK Agent with MCP Integration")
        print("=" * 50)
        print("Available MCPs:")
        for name, server in self.mcp_servers.items():
            print(f"  • {server['name']}: {server['description']}")
            print(f"    Tools: {', '.join(server['tools'])}")
        print("=" * 50)
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
                result = self.execute_request(user_input)
                
                # Display result
                if result.get("success"):
                    print(f"\n📊 Data: {json.dumps(result['data'], indent=2)}")
                else:
                    print(f"\n❌ Failed: {result.get('message', 'Unknown error')}")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")


def main():
    """Main function"""
    print("🔧 Initializing ADK Agent...")
    
    # Check if MCP servers are running
    agent = ADKAgent()
    
    # Test connection to MCP servers
    print("🔍 Checking MCP server connections...")
    for name, client in agent.mcp_clients.items():
        try:
            response = requests.get(f"{client.base_url}/", timeout=5)
            if response.status_code == 200:
                print(f"✅ {name}: Connected")
            else:
                print(f"⚠️  {name}: Unexpected status {response.status_code}")
        except requests.RequestException:
            print(f"❌ {name}: Not connected (make sure to start the MCP server)")
    
    print("\n" + "=" * 50)
    
    # Run interactive modeGOOGLE_API_KEY
    agent.run_interactive()


if __name__ == "__main__":
    main()