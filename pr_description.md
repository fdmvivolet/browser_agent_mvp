⚡ Optimize `_snapshot_line_for_ref` and `_snapshot_context_for_ref` functions

**What:**
Replaced `snapshot_yaml.splitlines()` with `str.find()` and `str.rfind()` inside `_snapshot_line_for_ref` and `_snapshot_context_for_ref` in `agent/safety.py`.

**Why:**
The previous implementation called `splitlines()` on the entire YAML snapshot string (which can be quite large for complex web pages). This allocated a massive array of strings just to find a single target line or small context window, resulting in wasted memory, high CPU usage, and slow performance on large strings.

**Measured Improvement:**
Benchmarking on a 10,000-line mock YAML snapshot shows a dramatic speedup:

- Original `_snapshot_line_for_ref`: **0.1656 s**
- Optimized `_snapshot_line_for_ref`: **0.0156 s** (10.6x faster)

- Original `_snapshot_context_for_ref`: **0.2127 s**
- Optimized `_snapshot_context_for_ref`: **0.0157 s** (13.5x faster)

These micro-optimizations reduce execution time overhead during agent safety checks, preventing CPU bottlenecks.

Refactored the agent to align with the "Orchestrator" persona and strict JSON architectural requirements.

**Changes:**
- Updated `agent/prompts.py` to enforce the DAG planning structure, MCP integration, HMT guidelines, and strict JSON output formats.
- Updated `agent/llm.py`'s `PlannerAction` Pydantic model to correctly handle fields like `thought_process`, `self_correction`, `action_type`, `dag_subgoals`, `mcp_request`, and `ag_ui_payload`.
- Rewrote the payload schemas for edge cases (missing API key, provider unavailable, JSON fallback).
- Updated `agent/core.py` to dispatch based on `action_type`.
- Updated `agent/tools.py` to handle the new action types.
- Fixed existing test specs to work with the updated JSON shapes.
