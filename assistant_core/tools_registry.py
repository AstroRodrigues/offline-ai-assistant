from pathlib import Path
from typing import List

from pydantic import BaseModel
import yaml

# this file laods the tools.yaml config file, validates every tool with pydantic(makes sure all fields are present and corect),
#  keeps everything organized(toolconfig =one tool, toolsconfig = all tools, list_tools =  safe way to get all tools)
# load_tools_config() reads the tools.yaml file and returns a ToolsConfig object

class ToolConfig(BaseModel):
    name: str
    description: str
    service: str
    endpoint: str
    enabled: bool = True


class ToolsConfig(BaseModel):
    tools: List[ToolConfig]


def load_tools_config() -> ToolsConfig:
    """
    Load the tools.yaml configuration file.
    This is the single source of truth for tool definitions.
    """
    root = Path(__file__).resolve().parents[1]
    config_path = root / "configs" / "tools.yaml"

    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return ToolsConfig(**raw)


# Load once at startup
tools_config = load_tools_config()


def list_tools(enabled: bool | None = None) -> List[ToolConfig]:
    """
    Return all tools, or only enabled/disabled tools.
      - enabled=True → only enabled tools
      - enabled=False → only disabled tools
      - enabled=None → all tools
    """
    if enabled is None:
        return tools_config.tools

    return [t for t in tools_config.tools if t.enabled == enabled]
