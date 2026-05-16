from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.markup import escape


def compact_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, default=str)


TOOL_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "goto": {
        "kind": "mutating",
        "args": '{"url": "string"}',
        "description": "Navigate the current tab to a URL.",
    },
    "observe": {
        "kind": "read-only",
        "args": "{}",
        "description": "Refresh the current page observation.",
    },
    "query_page": {
        "kind": "read-only",
        "args": '{"question": "string"}',
        "description": "Ask a DOM/page analyst sub-agent a compact question about the current page.",
    },
    "click_element": {
        "kind": "mutating",
        "args": '{"ref": "string"}',
        "description": "Click one element by its current Playwright ARIA ref.",
    },
    "type_text": {
        "kind": "mutating",
        "args": '{"ref": "string", "text": "string", "submit": "boolean", "clear": "boolean"}',
        "description": "Fill or type text into an element by current ARIA ref, optionally pressing Enter.",
    },
    "press_key": {
        "kind": "mutating",
        "args": '{"key": "string"}',
        "description": "Press a keyboard key in the current browser context.",
    },
    "scroll": {
        "kind": "mutating",
        "args": '{"direction": "up|down"}',
        "description": "Scroll the visible page up or down.",
    },
    "wait": {
        "kind": "read-only",
        "args": '{"ms": "integer"}',
        "description": "Wait for a bounded number of milliseconds.",
    },
    "screenshot": {
        "kind": "read-only",
        "args": '{"full_page": "boolean"}',
        "description": "Save a screenshot under logs/screenshots.",
    },
    "extract_text": {
        "kind": "read-only",
        "args": '{"ref": "string|null"}',
        "description": "Extract visible text from a specific current ref or from the full page.",
    },
    "extract_dom": {
        "kind": "read-only",
        "args": '{"selector": "string"}',
        "description": "Extract raw DOM/HTML for a given CSS selector.",
    },
    "extract_css": {
        "kind": "read-only",
        "args": '{"selector": "string", "property": "string"}',
        "description": "Extract computed CSS property value for a given CSS selector.",
    },
    "dismiss_popup": {
        "kind": "mutating",
        "args": "{}",
        "description": "Attempt to auto-dismiss common pop-ups or overlays.",
    },
    "ask_user": {
        "kind": "read-only",
        "args": '{"question": "string"}',
        "description": "Ask the human for missing information or explicit confirmation.",
    },
    "done": {
        "kind": "read-only",
        "args": '{"summary": "string", "status": "success|failed|stopped_by_user"}',
        "description": "Finish the run and produce the final report.",
    },
}


def format_tool_descriptions() -> str:
    lines = []
    for name, meta in TOOL_DESCRIPTIONS.items():
        lines.append(
            f"- {name} ({meta['kind']}): args {meta['args']}. {meta['description']}"
        )
    return "\n".join(lines)


class ToolDispatcher:
    def __init__(
        self, browser: Any, llm_client: Any, console: Console | None = None
    ) -> None:
        self.browser = browser
        self.llm_client = llm_client
        self.console = console or Console()
        self.current_obs: dict[str, Any] | None = None

    def set_observation(self, obs: dict[str, Any]) -> None:
        self.current_obs = obs

    def dispatch(self, action: dict[str, Any]) -> dict[str, Any]:
        action_type = action.get("action_type")

        try:
            if action_type == "delegate_actor":
                subgoals = action.get("dag_subgoals", [])
                self.console.print(
                    "[bold purple]Orchestrator Delegating to Actor:[/bold purple] "
                    + str(subgoals)
                )
                return {
                    "ok": True,
                    "message": "delegated to actor successfully",
                    "data": {"subgoals": subgoals},
                }

            if action_type == "mcp_tool_call":
                mcp_req = action.get("mcp_request", {})
                self.console.print(
                    f"[bold magenta]MCP Tool Call:[/bold magenta] {mcp_req}"
                )
                return {
                    "ok": True,
                    "message": "mcp tool call successful",
                    "data": {"mcp_response": "simulated_success"},
                }

            if action_type == "ag_ui_interrupt":
                ag_ui = action.get("ag_ui_payload", {})
                return self.ask_user(str(ag_ui.get("reason", "AG-UI Interrupt")))

            if action_type == "goal_complete":
                return {
                    "ok": True,
                    "message": "goal completed",
                    "data": {
                        "summary": "Goal completed by Orchestrator",
                        "status": "success",
                    },
                }

            return {
                "ok": False,
                "message": f"unknown action_type: {action_type}",
                "data": {},
            }
        except Exception as exc:
            return {
                "ok": False,
                "message": f"tool dispatch failed: {action_type}",
                "data": {"error": str(exc)},
            }

    def query_page(self, question: str) -> dict[str, Any]:
        self.console.print("[bold cyan]DOM Sub-agent:[/bold cyan] Processing query...")
        self.console.print(f"[dim]Question:[/dim] {escape(question)}")
        if not self.current_obs:
            return {
                "ok": False,
                "message": "no current observation available",
                "data": {},
            }
        answer = self.llm_client.query_page(self.current_obs, question)
        if answer.get("ok"):
            self.console.print(
                f"[dim]Answer:[/dim] {escape(str(answer['data'].get('answer', '')))}"
            )
        return answer

    def ask_user(self, question: str) -> dict[str, Any]:
        # input() doesn't support rich markup, but we print it via console first to be safe and consistent
        self.console.print(f"[bold]Question:[/bold] {escape(question)}")
        from agent.core import wait_for_user_input

        answer = wait_for_user_input(question)
        return {"ok": True, "message": "user answered", "data": {"answer": answer}}
