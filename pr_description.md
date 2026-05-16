Refactored the agent to align with the "Orchestrator" persona and strict JSON architectural requirements.

**Changes:**
- Updated `agent/prompts.py` to enforce the DAG planning structure, MCP integration, HMT guidelines, and strict JSON output formats.
- Updated `agent/llm.py`'s `PlannerAction` Pydantic model to correctly handle fields like `thought_process`, `self_correction`, `action_type`, `dag_subgoals`, `mcp_request`, and `ag_ui_payload`.
- Rewrote the payload schemas for edge cases (missing API key, provider unavailable, JSON fallback).
- Updated `agent/core.py` to dispatch based on `action_type`.
- Updated `agent/tools.py` to handle the new action types.
- Fixed existing test specs to work with the updated JSON shapes.
