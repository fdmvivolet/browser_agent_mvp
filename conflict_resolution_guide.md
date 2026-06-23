# Guide to Resolve PR Conflicts

The following pull requests have conflicts with the `main` branch. Follow the instructions below to resolve them.

## PR: `origin/pr/12`
**Conflicting files:**
- `agent/browser.py`
- `agent/core.py`
- `agent/llm.py`
- `agent/prompts.py`
- `agent/safety.py`
- `pr_description.md`
- `tests/test_browser_ssrf.py`

### How to resolve:
1. Ensure your local repository is up to date:
   ```bash
   git checkout main
   git pull origin main
   git fetch origin
   ```
2. Check out the pull request branch locally (assuming it is PR #12):
   ```bash
   # For GitHub CLI:
   gh pr checkout 12
   # OR manually:
   git fetch origin pull/12/head:pr-12
   git checkout pr-12
   ```
3. Merge `main` into the PR branch:
   ```bash
   git merge main
   ```
4. Open the conflicting files in your editor and resolve the conflicts. Look for the `<<<<<<<`, `=======`, and `>>>>>>>` markers. Choose the correct code and remove the markers.
5. Stage the resolved files:
   ```bash
   git add "agent/browser.py" "agent/core.py" "agent/llm.py" "agent/prompts.py" "agent/safety.py" "pr_description.md" "tests/test_browser_ssrf.py"
   ```
6. Commit the merge:
   ```bash
   git commit
   ```
7. Push the changes to update the pull request:
   ```bash
   git push origin HEAD
   ```
