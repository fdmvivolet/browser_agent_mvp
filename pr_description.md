Resolves all open pull requests and merge conflicts.

This PR consolidates and successfully resolves conflicts for all recent feature and fix branches, including:
- Updating system prompts (`agent/prompts.py`) to include the new Orchestrator and Validator definitions.
- Refactoring `agent/llm.py` to use Pydantic models for the PlannerAction schema.
- Fixing DOM XSS vulnerabilities in `templates/index.html`.
- Adding robust database persistence tests to `tests/test_memory.py`.
- Adding popup dismissal tests to `tests/test_browser_dismiss_popup.py`.
- Fixing unused imports across the repository.

Care was taken during the resolution to preserve `from __future__ import annotations` and ensure the `agent/core.py` and `tests/test_browser_ssrf.py` remained unchanged by conflicting PRs.
