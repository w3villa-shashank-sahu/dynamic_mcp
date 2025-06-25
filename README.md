# MCP + ADK Sample Project

This project demonstrates a simple MCP (Model Context Protocol) + ADK (Agent Development Kit) setup with two MCP servers and an AI agent that can select and use tools from these MCPs.

## Project Structure

```
├── requirements.txt
├── .env.example
├── README.md
├── main.py                 # Main ADK agent application
├── mcp_servers/
│   ├── weather_mcp.py      # Weather MCP server
│   └── calculator_mcp.py   # Calculator MCP server
├── tools/
│   ├── weather_tools.py    # Weather MCP tools
│   └── calculator_tools.py # Calculator MCP tools
└── config/
    └── mcp_config.json     # MCP server configuration
```

## Features

- **Weather MCP**: Contains `getWeather` and `getTime` tools
- **Calculator MCP**: Contains `addNumber` and `subtractNumber` tools
- **AI Agent**: Uses Google Gemini to intelligently select MCPs and tools based on user prompts

## Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your Google API key
   ```

3. **Start the MCP servers**:
   ```bash
   # Terminal 1: Start Weather MCP
   python mcp_servers/weather_mcp.py
   
   # Terminal 2: Start Calculator MCP
   python mcp_servers/calculator_mcp.py
   ```

4. **Run the main application**:
   ```bash
   python main.py
   ```

## Usage

1. Start the MCP servers in separate terminals
2. Run the main application
3. Enter your prompt in the terminal
4. The AI agent will:
   - Analyze your prompt
   - Select the appropriate MCP
   - Choose the right tool
   - Execute the tool and return results

## Example Prompts

- "What's the weather like today?" → Weather MCP → getWeather tool
- "What time is it?" → Weather MCP → getTime tool
- "Add 5 and 3" → Calculator MCP → addNumber tool
- "Subtract 10 from 25" → Calculator MCP → subtractNumber tool

## MCP Tools

### Weather MCP Tools
- `getWeather`: Returns current weather information (dummy data)
- `getTime`: Returns current time information (dummy data)

### Calculator MCP Tools
- `addNumber`: Adds two numbers together
- `subtractNumber`: Subtracts the second number from the first

## Configuration

The MCP servers are configured in `config/mcp_config.json` with their respective ports and tool definitions. 