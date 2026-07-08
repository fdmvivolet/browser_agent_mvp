# Pull Request Summaries

## Refactor: adopt Orchestrator persona and strict JSON schema
Refactored the agent to align with the "Orchestrator" persona and strict JSON architectural requirements.

**Changes:**
- Updated `agent/prompts.py` to enforce the DAG planning structure, MCP integration, HMT guidelines, and strict JSON output formats.
- Updated `agent/llm.py`'s `PlannerAction` Pydantic model to correctly handle fields like `thought_process`, `self_correction`, `action_type`, `dag_subgoals`, `mcp_request`, and `ag_ui_payload`.
- Rewrote the payload schemas for edge cases (missing API key, provider unavailable, JSON fallback).
- Updated `agent/core.py` to dispatch based on `action_type`.
- Updated `agent/tools.py` to handle the new action types.
- Fixed existing test specs to work with the updated JSON shapes.

## Security: Fix DOM-based XSS vulnerability in action logs and facts rendering

🎯 **What:** The vulnerability fixed
The `templates/index.html` file contained two DOM-based Cross-Site Scripting (XSS) vulnerabilities. Specifically, the "Using tool" action logs (line 493) and the facts list (line 551) assigned dynamic, untrusted data directly to the `innerHTML` property of dynamically generated DOM elements.

⚠️ **Risk:** The potential impact if left unfixed
Untrusted data originating from LLM output, website interactions, or tool logs could contain malicious HTML or JavaScript sequences (such as `<script>alert('xss')</script>`). Because `innerHTML` processes HTML strings natively, the application would execute arbitrary scripts in the context of the user's browser, potentially leading to session hijacking, unauthorized actions on behalf of the user, or defacement.

🛡️ **Solution:** How the fix addresses the vulnerability
The assignments to `innerHTML` were replaced with secure DOM API usage. Specifically:
- `document.createElement()` was used to safely create new `<strong>` and `<span>` elements.
- `innerText` and `document.createTextNode()` were used to insert the textual content (both the hardcoded prefixes and the dynamic variable data) to ensure the browser strictly interprets the inserted data as textual content rather than executable code.

No new dependencies were introduced, and the UI styles and functionality remain completely unchanged while completely mitigating the XSS vector. Testing included verifying against `pytest` tests, a temporary Playwright test asserting secure DOM rendering, and running code formatters and linters successfully.
