import json
import os
import re
from dataclasses import dataclass, field
from typing import Literal

from minisweagent.integrations.github_mcp import MCPTools
from prompt_toolkit.history import FileHistory
from prompt_toolkit.shortcuts import PromptSession
from rich.console import Console

from minisweagent import global_config_dir
from minisweagent.agents.interactive import InteractiveAgent, InteractiveAgentConfig

console = Console(highlight=False)
prompt_session = PromptSession(history=FileHistory(global_config_dir / "interactive_history.txt"))


@dataclass
class MCPAgentConfig(InteractiveAgentConfig):
    enable_mcp_tools: bool = True
    mcp_tool_choice: Literal["auto", "manual"] = "auto"
    github_token: str = field(default_factory=lambda: os.environ.get("GITHUB_TOKEN", ""))


class MCPAgent(InteractiveAgent):
    def __init__(self, *args, config_class=MCPAgentConfig, **kwargs):
        super().__init__(*args, config_class=config_class, **kwargs)
        self.mcp_tools = MCPTools(self.config)
        self.extra_template_vars["mcp_tools_info"] = self.mcp_tools.available_tools() if self.config.enable_mcp_tools else ""

    def parse_action(self, response: dict) -> dict:
        if self.config.enable_mcp_tools and (mcp_match := re.search(r"@mcp_call(\{.*\})", response["content"], re.DOTALL)):
            call_data = json.loads(mcp_match.group(1))
            return {"action_type": "mcp", "tool": call_data["tool"], "args": call_data["args"], **response}
        return super().parse_action(response)

    def execute_action(self, action: dict) -> dict:
        if action.get("action_type") != "mcp":
            return super().execute_action(action)
        return {"output": json.dumps(self.mcp_tools.execute_mcp_tool(action["tool"], action["args"]), indent=2), "exit_code": 0}
    
    def __del__(self):
        pass