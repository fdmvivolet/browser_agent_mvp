# PR Conflict Resolution Guide

This repository currently has 17 open Pull Requests. When attempting to merge them all together sequentially (ordered by PR number), a merge conflict arises in `templates/index.html`.

Here is how to resolve this conflict:

## 1. `templates/index.html` (PR #35 vs PR #38)
Both PR #35 ("Fix DOM-based XSS vulnerability in action logs") and PR #38 ("Fix DOM XSS vulnerabilities in index.html") attempt to fix the exact same DOM-based XSS issue where untrusted string variables were being assigned to `.innerHTML`.

- **The Conflict:** They implemented slightly different secure alternatives. PR #35 used `document.createElement("strong")` and `.innerText`, while PR #38 used `document.createElement('strong')` and `.textContent`.
- **Resolution:** When merging, simply choose one of the two PRs' implementations (e.g., choose PR #38's changes) and discard the other. Both achieve the same security goal safely.
