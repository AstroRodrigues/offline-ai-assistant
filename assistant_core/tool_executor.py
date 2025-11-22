import json
import re
import httpx
from typing import Any, Dict, Optional, Tuple

from .tools_registry import list_tools


TOOL_CALL_RE = re.compile(
    r"^CALL_TOOL:\s*(?P<name>[a-zA-Z0-9_.-]+)\s*\nARGS:\s*(?P<args>\{.*\})\s*$",
    re.DOTALL
)


def parse_tool_call(text: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    If text matches the tool-call contract, return (tool_name, args_dict).
    Otherwise return None.
    """
    m = TOOL_CALL_RE.match(text.strip())
    if not m:
        return None

    name = m.group("name").strip()
    args_raw = m.group("args").strip()

    try:
        args = json.loads(args_raw)
        if not isinstance(args, dict):
            return None
    except json.JSONDecodeError:
        return None

    return name, args


def execute_tool(tool_name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a tool by name using tools.yaml registry.
    Raises ValueError if tool not found/enabled.
    """
    tools = {t.name: t for t in list_tools(enabled=True)}

    if tool_name not in tools:
        raise ValueError(f"Tool '{tool_name}' not found or disabled.")

    tool = tools[tool_name]

    # If endpoint is relative (like /tool/ping), assume assistant_core
    endpoint = tool.endpoint
    if endpoint.startswith("/"):
        url = f"http://127.0.0.1:8000{endpoint}"
    else:
        url = endpoint

    # Simple POST by default if args exist, otherwise GET.
    try:
        if args:
            resp = httpx.post(url, json=args, timeout=30.0)
        else:
            resp = httpx.get(url, timeout=30.0)
        resp.raise_for_status()
    except httpx.RequestError as e:
        return {"error": "tool_unreachable", "detail": str(e)}
    except httpx.HTTPStatusError as e:
        return {"error": "tool_http_error", "status_code": e.response.status_code}

    return resp.json()
