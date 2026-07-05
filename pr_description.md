## Resolve all PRs

This PR integrates multiple outstanding feature, security, and performance PRs:
- **Security**: Fixes DOM XSS vulnerabilities in `templates/index.html` by safely rendering action logs and facts using DOM elements instead of string concatenation.
- **Security**: Disables insecure Flask configuration by defaulting `app.run(debug=False)`.
- **Performance**: Optimizes `Browser.dismiss_popup()` sequential blocking checks by combining selectors.
- **Performance**: Optimizes `agent/memory.py` by using `executemany` for batch database facts merging.
- **Refactoring**: Updates orchestrator, subagent, and validator prompts in `agent/prompts.py` for clearer behavioral boundaries.
- **Testing**: Adds comprehensive tests for `Browser.dismiss_popup` and `Memory.merge_facts`.
- **Code Health**: Cleans up unused imports across the codebase (`run.py`, `agent/memory.py`, `agent/prompts.py`, `agent/safety.py`, `scripts/smoke_openrouter.py`).

All conflicts during the merge process were carefully resolved by favoring security and performance patches.
