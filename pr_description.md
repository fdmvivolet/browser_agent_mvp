Merge All PRs resolving Conflicts

This branch resolves the merge conflicts among multiple pull requests affecting `agent/prompts.py`, `templates/index.html`, `tests/test_browser_dismiss_popup.py`, and `agent/memory.py`.

It includes the changes to:
- Add a new VALIDATOR_PROMPT.
- Refactor the Orchestrator SYSTEM_PROMPT.
- Update the Actor Agent SUBAGENT_PROMPT.
- Improve testing for Memory.merge_facts and Browser.dismiss_popup.
- Fix XSS vulnerabilities in `templates/index.html`.
- Remove unused imports across various modules (`agent/prompts.py`, `agent/safety.py`, `app.py`, `run.py`).
- Implement optimizations for sqlite3 memory database (`executemany`) and concurrent UI checks (`dismiss_popup`).
- Re-added `from __future__ import annotations` inside files using `|` union type hints to prevent breaking older Python versions (3.9 and earlier).
