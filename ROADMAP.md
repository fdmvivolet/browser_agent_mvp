# Roadmap: Browser Agent MVP to Production-Grade Enterprise System

This roadmap outlines the strategic evolution of the browser agent from its current MVP state—a deterministic, linear, ARIA-dependent script—into a resilient, probabilistic, and perception-driven cognitive architecture.

## 1. Component-Based Improvements & Architectural Analysis

### 1.1 Perception & Actuation
**Current State (MVP):**
Relies exclusively on ARIA accessibility snapshots (`page.locator("body").aria_snapshot(mode="ai")`). It cannot perceive visual layouts, `canvas` elements, or non-semantic DOM elements (like a `div` acting as a button without `role="button"`). Single-tab constraints severely limit multi-source workflows.

**Target Architecture:**
Hybrid perception paradigm. Implement Vision-Language Model (VLM) fallbacks (e.g., GPT-4o vision or similar) for pixel-based reasoning, and deep programmatic DOM/CSS inspection (e.g., computing `z-index`, `opacity`, and visibility via `page.evaluate()`). Additionally, add advanced handling for Declarative Shadow DOMs and dynamic overlay blocking at the network layer.

**Code Architecture Shift (Conceptual `agent/browser.py` update):**
```python
<<<<<<< SEARCH
    def observe(self) -> dict[str, Any]:
        page = self._page()
        snapshot = ""
        # ...
        try:
            snapshot = page.locator("body").aria_snapshot(mode="ai")
        except Exception as exc:  # Playwright can raise browser-specific errors.
            error = f"ARIA snapshot failed: {exc}"
=======
    def observe(self) -> dict[str, Any]:
        page = self._page()
        snapshot = ""
        visual_fallback_triggered = False

        # 1. Network-Level Ad/Banner Blocking
        # self.context.route("**/*", block_tracker_scripts)

        # 2. Try primary semantic extraction
        try:
            # Wait for shadow hosts to attach
            page.wait_for_function("() => document.querySelector('body') !== null")
            snapshot = page.locator("body").aria_snapshot(mode="ai")

            # Validate snapshot quality; if poor, trigger fallback
            if self._requires_visual_fallback(snapshot):
                visual_fallback_triggered = True

        except Exception as exc:
            error = f"ARIA snapshot failed: {exc}"
            visual_fallback_triggered = True

        # 3. DOM/CSS Programmatic Fallback (Shadow DOM & Z-Index awareness)
        dom_inspection_data = {}
        if visual_fallback_triggered:
            dom_inspection_data = page.evaluate("""
                () => {
                   // Inject JS to compute visibility, z-index, and extract non-ARIA interactive nodes
                   // Piercing shadow roots dynamically.
                   return extractInteractiveNodesFallback();
                }
            """)

        # ... (Capture high-res VLM screenshot if needed)
>>>>>>> REPLACE
```

### 1.2 Memory & Context
**Current State (MVP):**
A rigid, 8-step fixed sliding window (`self.history: deque[dict[str, Any]] = deque(maxlen=8)` in `agent/memory.py`). Causes the agent to suffer from severe amnesia during long-horizon tasks, dropping initial instructions or earlier layout discoveries.

**Target Architecture:**
Retrieval-Augmented Generation (RAG) combined with Hierarchical Memory Trees (HMT). Break memory into three tiers: Intent Level (global goal), Stage Level (workflow phase), and Action Level (specific interactions). Store state-action tuples in an embedded vector database (e.g., FAISS) to allow near-infinite contextual recall without blowing up LLM context limits.

**Code Architecture Shift (Conceptual `agent/memory.py` update):**
```python
<<<<<<< SEARCH
class Memory:
    def __init__(self, goal: str, db_path: str = "memory.db") -> None:
        self.goal = goal
        self.facts: dict[str, str] = {}
        self.history: deque[dict[str, Any]] = deque(maxlen=8)
        self.current_obs: dict[str, Any] | None = None
        self.step = 0
=======
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class HierarchicalMemoryTree:
    def __init__(self, goal: str, db_path: str = "memory.db") -> None:
        self.global_intent = goal
        self.current_stage = "INITIALIZATION"

        # Vector DB replacing fixed deque
        self.embedding_model = SentenceTransformer('jinaai/jina-embeddings-v2-base-en')
        self.action_index = faiss.IndexFlatL2(768)
        self.memory_store = [] # Map index to data

        self.current_obs: dict[str, Any] | None = None
        self.step = 0

    def add_action(self, action: dict[str, Any], result: dict[str, Any], obs_hash: str) -> None:
        self.step += 1
        record = {
            "stage": self.current_stage,
            "step": self.step,
            "thought": action.get("thought"),
            "tool": action.get("tool"),
            "dom_hash": obs_hash
        }
        # Vectorize and store
        vector = self.embedding_model.encode([str(record)])
        self.action_index.add(np.array(vector).astype('float32'))
        self.memory_store.append(record)

    def retrieve_relevant_context(self, current_dom_state: str) -> list[dict]:
        # Perform semantic search to retrieve ONLY relevant past actions for the current DOM state
        # instead of a blind sliding window.
        pass
>>>>>>> REPLACE
```

### 1.3 Planning, Execution & Resilience
**Current State (MVP):**
Linear `observe -> decide -> act` loop managed in `agent/core.py`. A single Orchestrator LLM handles both high-level semantic planning and low-level DOM interaction. Highly susceptible to the "Agent Loop Problem" (Repeaters, Wanderers, Loopers) when hitting invisible overlays.

**Target Architecture:**
**Planner-Actor-Validator Swarm Architecture.**
1.  **Orchestrator (Planner):** Generates an Abstract Syntax Tree (AST) or DAG of sub-goals based entirely on semantic context, decoupled from the heavy DOM.
2.  **Actor (Browser Agent):** A localized sub-agent given only the current sub-goal and immediate DOM state to execute physical interactions.
3.  **Validator:** Evaluates if the Actor achieved the Orchestrator's sub-goal.
Also requires **deterministic stuck-state detection** using cryptographic hashing of the DOM viewport to break infinite loops.

**Code Architecture Shift (Conceptual `agent/core.py` update):**
```python
<<<<<<< SEARCH
    for current_goal in sub_goals:
        # ...
        try:
            goal_completed = False
            while not goal_completed:
                # ...
                obs = browser.observe()
                action = llm.plan(memory.to_prompt_payload(), memory.get_current_screenshot())
                result = _execute_with_safety(action, obs, tools, console)
=======
    # Planner-Actor-Validator Architecture
    orchestrator = OrchestratorAgent(llm_client)
    execution_plan_dag = orchestrator.generate_plan(goal)

    for sub_task in execution_plan_dag:
        actor_agent = ActorAgent(llm_client, task=sub_task)
        validator_agent = ValidatorAgent(llm_client)

        task_completed = False
        while not task_completed:
            obs = browser.observe()
            current_dom_hash = hash_dom(obs)

            # 1. Stuck-State Heuristic Detection
            if memory.is_stuck(current_dom_hash, recent_actions):
                trigger_self_reflection_or_hitl()

            # 2. Actor executes narrowly focused step
            action = actor_agent.decide_next_step(obs)
            result = _execute_with_safety(action, obs, tools, console)

            # 3. Validator checks if sub_task condition is met
            validation_result = validator_agent.evaluate(sub_task, obs, result)
            if validation_result.is_success:
                task_completed = True
            elif validation_result.requires_replanning:
                execution_plan_dag = orchestrator.replan(validation_result.reason)
                break
>>>>>>> REPLACE
```

### 1.4 UI/UX & Ecosystem Integrations
**Current State (MVP):**
Terminal-based CLI utilizing Python `rich` logging. No external tool abstraction.

**Target Architecture:**
1.  **Model Context Protocol (MCP):** Abstract all file system access, database queries, and 3rd party APIs into an MCP server to drastically reduce context window token bloat and prevent tool hallucination.
2.  **AG-UI Protocol & Multi-Pane Dashboard:** Transition to a React-based frontend using Server-Sent Events (SSE). Use a multi-pane layout separating "Agent Thinking" (collapsible logs, e.g., AgentPrism) from "Agent Action" (live iframe/WebRTC browser stream).
3.  **Human-in-the-Loop (HITL):** Implement structured Copilot-style overrides, allowing users to seamlessly resolve CAPTCHAs or MFA prompts and inject context without crashing the agent.
4.  **Google Stitch `DESIGN.md`:** Ensure all dynamically generated UI components adhere to a centralized design system specification for pixel-perfect brand consistency.

---

## 2. Strategic Roadmap

### Stage 1: Stability and Perception Upgrade (Months 1-2)
**Objective:** Eliminate structural fragility, upgrade perception, and bypass the 8-step memory limit.
*   **Implement Hybrid Perception:** Integrate VLM fallback and programmatic DOM/CSS inspection (`page.evaluate()`) to handle `canvas`, shadow roots, and hidden states.
*   **Establish RAG Memory Layer:** Replace the 8-step sliding window with a localized vector DB (e.g., FAISS). Implement Hierarchical Memory Trees (Intent → Stage → Action).
*   **Deploy Stuck-State Heuristics:** Implement deterministic DOM hashing. Pause execution and force LLM self-reflection if identical states or action loops are detected.

### Stage 2: Cognitive Restructuring and Protocol Integration (Months 3-4)
**Objective:** Enable complex long-horizon planning, orchestrate multiple tabs, and decouple tool execution.
*   **Architect Hierarchical Planning:** Refactor `core.py` into a Planner-Actor-Validator model. Isolate high-level reasoning from localized DOM interaction.
*   **Implement Model Context Protocol (MCP):** Offload external tool schemas (databases, filesystems) to an independent MCP server.
*   **Enable Multi-Tab Concurrency:** Upgrade Playwright integration to explicitly manage isolated `BrowserContexts`, allowing sub-agents to process disparate tabs in parallel.

### Stage 3: Observability and Enterprise UI/UX (Months 5-6)
**Objective:** Build a secure, transparent, and visually coherent interface with robust HITL capabilities.
*   **Adopt AG-UI Protocol:** Transition from CLI to an event-driven SSE architecture, streaming `RunStarted`, `ToolCallStart`, and `StateDelta` to the frontend.
*   **Develop Multi-Pane Dashboard:** Build a React UI featuring chat, status cards, and a live execution pane. Use tools like AgentPrism to visualize JSON traces cleanly.
*   **Implement Structured HITL:** Allow the UI to securely pause execution for manual CAPTCHA solving or MFA injection, smoothly passing control back to the Orchestrator.
*   **Integrate DESIGN.md:** Add Google Stitch specifications to the root directory so AI-generated UI components perfectly match enterprise branding automatically.
