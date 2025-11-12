"""MCP-aware agent that can use GitHub MCP tools alongside bash commands.

This agent extends InteractiveAgent to support MCP tool calling while maintaining
the simplicity of mini-swe-agent's design philosophy.
"""

import json
import logging
import re
from dataclasses import dataclass

from minisweagent.agents.interactive import InteractiveAgent, InteractiveAgentConfig
from minisweagent.integrations.github_mcp import GitHubMCPClient, MCPToolConfig

logger = logging.getLogger(__name__)


@dataclass
class MCPAgentConfig(InteractiveAgentConfig):
    """Configuration for MCP-aware agent."""

    enable_mcp_tools: bool = True
    """Whether to enable MCP tools."""
    mcp_tool_choice: str = "auto"
    """Tool choice strategy: 'auto', 'bash_only', 'mcp_preferred'."""
    system_template: str = """You are a helpful AI assistant with access to both bash commands and GitHub MCP tools.

You can execute bash commands OR use GitHub MCP tools to interact with repositories.

For GitHub operations, you can either:
1. Use MCP tools by calling them with JSON format: @mcp_call{{"tool": "tool_name", "args": {{...}}}}
2. Use bash commands with gh CLI or curl

Choose the approach that best fits the task. Bash is often simpler and more flexible.
"""
    instance_template: str = """Your task: {{task}}

{{mcp_tools_info}}

Please reply with a single shell command in triple backticks OR an MCP tool call.
To finish, the first line of the output of the shell command must be 'COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'.
"""


class MCPAgent(InteractiveAgent):
    """Agent with MCP tool calling capabilities.
    
    This agent can use GitHub MCP tools in addition to bash commands,
    providing a more structured interface to GitHub operations when needed.
    """

    def __init__(self, *args, mcp_config: MCPToolConfig | None = None, config_class=MCPAgentConfig, **kwargs):
        super().__init__(*args, config_class=config_class, **kwargs)
        self.mcp_client = GitHubMCPClient(mcp_config)
        self.extra_template_vars["mcp_tools_info"] = (
            self.mcp_client.format_tools_for_prompt() if self.config.enable_mcp_tools else ""
        )

    def parse_action(self, response: dict) -> dict:
        """Parse action from response, supporting both bash and MCP tool calls."""
        # Try to parse MCP tool call first
        if self.config.enable_mcp_tools:
            # Look for @mcp_call followed by JSON
            content = response["content"]
            mcp_match = re.search(r"@mcp_call(\{.*\})", content, re.DOTALL)
            if mcp_match:
                json_str = mcp_match.group(1)
                return self._parse_mcp_call(json_str, response)

        # Fall back to standard bash parsing
        return super().parse_action(response)

    def _parse_mcp_call(self, call_str: str, response: dict) -> dict:
        """Parse an MCP tool call from the response."""
        try:
            call_data = json.loads(call_str)
            return {"action_type": "mcp", "tool": call_data["tool"], "args": call_data["args"], **response}
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse MCP call: {e}")
            return super().parse_action(response)

    def execute_action(self, action: dict) -> dict:
        """Execute action - either bash command or MCP tool call."""
        if action.get("action_type") == "mcp":
            return self._execute_mcp_action(action)
        return super().execute_action(action)

    def _execute_mcp_action(self, action: dict) -> dict:
        """Execute an MCP tool call."""
        tool_name = action["tool"]
        args = action["args"]

        logger.info(f"Executing MCP tool: {tool_name}")

        try:
            result = self.mcp_client.execute_tool(tool_name, args)
            output_str = json.dumps(result, indent=2)
            return {"output": output_str, "exit_code": 0}
        except Exception as e:
            logger.error(f"MCP tool execution failed: {e}")
            return {"output": f"Error executing MCP tool: {e}", "exit_code": 1}
