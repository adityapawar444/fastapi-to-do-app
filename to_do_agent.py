from mcp.client.streamable_http import streamablehttp_client
from strands.tools.mcp.mcp_client import MCPClient
from strands import Agent
from strands.models.gemini import GeminiModel


SYSTEM_PROMPT = """You are a helpful todo list assistant. You help users manage their tasks efficiently.

Key capabilities:
- Create new tasks with titles, descriptions, priorities (urgent/high/medium/low), and optional due dates
- List and search tasks by status (pending/inprogress/completed), priority, or text search
- Update task details including status, priority, or due dates
- Delete tasks when no longer needed
- Get details of specific tasks by ID

Guidelines:
- When users mention relative times like "tomorrow" or "next week", convert them to actual ISO datetime strings
- For task status, use: pending, inprogress, or completed
- For priority, use: urgent, high, medium, or low
- Be conversational and friendly
- If a task operation succeeds, confirm it clearly to the user
- If you need more information to complete a task, ask the user
- When showing multiple tasks, present them in a clear, organized way
- Do Not show ID to User
"""

def main():
    """Main function to run the todo agent"""
    
    print("=" * 60)
    print(">>> TODO AGENT - Powered by Google Gemini & MCP")
    print("=" * 60)
    print("\nInitializing agent and connecting to MCP server...")
    
    google_api_key = ""
    if not google_api_key:
        raise Exception("Missing API KEY")
    
    model = GeminiModel(
        client_args={
            "api_key": google_api_key,
        },
        model_id="gemini-2.5-flash",
        params={ 
            "temperature": 0.7,
            "max_output_tokens": 2048, # try OpenRouter
            "top_p": 0.9,
            "top_k": 40
        }
    )
    
    system_prompt = SYSTEM_PROMPT

    def create_streamable_http_transport():
        return streamablehttp_client("http://localhost:8000/mcp/")

    streamable_http_mcp_client = MCPClient(create_streamable_http_transport)
    
    with streamable_http_mcp_client as mcp_client:
        
        tools = mcp_client.list_tools_sync()
        print(f"Connected to MCP server")
        print(f"Available tools: {[tool.tool_name for tool in tools]}\n")
        
        agent = Agent(
            name="TodoAgent",
            model=model,
            system_prompt=system_prompt,
            tools=tools
        )
        
        print("Agent initialized successfully!\n")
        print("You can now interact with your todo list.")
        print("Examples:")
        print("  - 'Create a task to buy groceries with high priority'")
        print("  - 'Show me all pending tasks'")
        print("  - 'Mark task XYZ as completed'")
        print("  - 'What are my urgent tasks?'")
        print("\nType 'exit' or 'quit' to stop.\n")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() in ['exit']:
                    print("\n Goodbye! Your tasks are saved.")
                    break
                
                print("\n Agent: ", end="", flush=True)
                
                response = agent(user_input)                
                print(response)
                
            except KeyboardInterrupt:
                print("\n\n Keyborad Interrupt.....")
                break
            except Exception as e:
                print(f"\n Error: {str(e)}")
                print("Please try again or type 'quit' to exit.")

if __name__ == "__main__":
    main()