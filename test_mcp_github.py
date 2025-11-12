#!/usr/bin/env python3
"""
Test the MCP agent with real GitHub operations.
This demonstrates how to use the GitHub MCP tools with mini-swe-agent.
"""

import os
import tempfile
from pathlib import Path

def create_test_scenario():
    """Create a simple test scenario to verify MCP agent works."""
    
    # Create a temporary task file
    task = """Please help me understand the mini-swe-agent repository:

1. First, use bash commands (gh CLI or curl) to list some recent issues in the SWE-agent/mini-swe-agent repository
2. Then try using an MCP tool to search for repositories related to "swe-agent" 
3. Show me the differences between using bash commands vs MCP tools for GitHub operations

You can use either approach - the goal is to demonstrate both methods work.
When you're done exploring, use: echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT"""
    
    return task

def run_mcp_test_with_github_token():
    """Instructions for running with a real GitHub token."""
    
    print("=== Testing MCP Agent with GitHub Operations ===\n")
    
    print("To test the GitHub MCP integration properly, you need:")
    print("1. A GitHub token (for authentication)")
    print("2. An LLM API key (OpenAI, Anthropic, etc.)")
    print()
    
    # Check if GitHub token is available
    github_token = os.getenv("GITHUB_TOKEN")
    if not github_token:
        print("❌ GITHUB_TOKEN not found in environment")
        print("   Set it with: export GITHUB_TOKEN=your_token_here")
    else:
        print("✅ GITHUB_TOKEN found in environment")
    
    # Check for API keys
    api_keys = {
        "OpenAI": os.getenv("OPENAI_API_KEY"),
        "Anthropic": os.getenv("ANTHROPIC_API_KEY"),
        "Gemini": os.getenv("GEMINI_API_KEY"),
    }
    
    found_keys = [name for name, key in api_keys.items() if key]
    if found_keys:
        print(f"✅ Found API keys for: {', '.join(found_keys)}")
    else:
        print("❌ No LLM API keys found")
        print("   Set one with: export OPENAI_API_KEY=your_key_here")
    
    print("\n=== Ready to test? ===")
    
    # Create the test task
    task = create_test_scenario()
    
    print("Here are the commands you can run to test:")
    print()
    
    # Test 1: Interactive mode
    print("## Test 1: Interactive Mode (with confirmations)")
    print("mini-mcp")
    print("# Then paste this task when prompted:")
    print(f'"""{task}"""')
    print()
    
    # Test 2: Direct mode  
    print("## Test 2: Direct Mode (bypass prompts)")
    print(f'mini-mcp -y -t "{task.strip()}"')
    print()
    
    # Test 3: With specific model
    print("## Test 3: With Specific Model")
    print(f'mini-mcp -m gpt-4o -t "{task.strip()}"')
    print()
    
    # Test 4: Disable MCP tools (fallback to bash only)
    print("## Test 4: Disable MCP Tools (Bash Only)")
    print(f'mini-mcp --disable-mcp -t "{task.strip()}"')
    print()
    
    print("=== Example Expected Behavior ===")
    print()
    print("The agent should:")
    print("1. Use 'gh' CLI commands to list GitHub issues")
    print("2. Try MCP tools like @mcp_call for repository search")
    print("3. Show you the differences between both approaches")
    print("4. Complete the task successfully")
    print()
    
    print("=== Troubleshooting ===")
    print()
    print("If you get errors:")
    print("- Check that 'gh' CLI is installed and authenticated")
    print("- Verify your GitHub token has proper permissions")
    print("- Make sure your LLM API key is valid")
    print("- Try with --disable-mcp to test bash-only mode first")

def test_mcp_tools_directly():
    """Test MCP tools directly without running the full agent."""
    print("\n=== Testing MCP Tools Directly ===\n")
    
    from minisweagent.integrations.github_mcp import GitHubMCPClient, MCPToolConfig
    
    # Test the MCP client directly
    config = MCPToolConfig(
        github_token=os.getenv("GITHUB_TOKEN"),
        enabled_tools=["search_repositories", "list_issues", "get_file_contents"]
    )
    
    client = GitHubMCPClient(config)
    
    print(f"Available tools: {[t['function']['name'] for t in client.get_tools()]}")
    print()
    
    # Test tool execution (this will show the placeholder behavior)
    print("Testing tool execution:")
    result = client.execute_tool("search_repositories", {"query": "swe-agent"})
    print(f"Result: {result}")
    print()
    
    print("Note: The current implementation uses placeholder responses.")
    print("This demonstrates that the MCP infrastructure is working.")
    print("In a full implementation, these would make real GitHub API calls.")

if __name__ == "__main__":
    run_mcp_test_with_github_token()
    test_mcp_tools_directly()