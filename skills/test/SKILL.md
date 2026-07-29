---
name: "test"
description: "The Test Quality Protocol. Defines how to write, run, and verify tests to prevent self-verification bias."
environment_target: "universal"
priority: 2
---
# The Test Quality Protocol

**Trigger**: Loaded by `/execute` for any task that involves writing or modifying code. Also loaded explicitly by `/loop` as the termination gate.

> [!CAUTION]
> **Self-Verification Bias**: A model that writes code AND writes its own tests is biased. It will test the path it built, not the requirement it was given. This protocol exists to break that bias.

> [!NOTE]
> Check your orchestrator tier banner (`[TIER: X]`). This determines the complexity and scope of the tests you should write.

---

## Index
1. [Step 1: Test-First Mandate (TDD)](#1-test-first-mandate)
2. [Step 2: Tier-Aware Test Scope](#2-tier-aware-test-scope)
3. [Step 3: The 3-Test Rule](#3-the-3-test-rule)
4. [Step 4: Static Analysis Gate](#4-static-analysis-gate)
5. [Step 5: Integration Smoke Test](#5-integration-smoke-test)
6. [Step 6: Visual Verification Protocol](#6-visual-verification-protocol)
7. [Forbidden Test Patterns](#forbidden-test-patterns)

---

## 1. Test-First Mandate

Tests MUST be written from the spec or task `<done>` criteria BEFORE any implementation code is written.

**The rule**: Close all implementation files. Read only the spec or `<done>` criteria. Write the tests. Only then open the implementation.

If tests are written after code, they are invalid — they test the implementation, not the requirement.

---

## 2. Tier-Aware Test Scope

Before writing tests, check your tier:
- **[TIER: SMALL]**: You MUST write simple, highly focused tests. Avoid creating complex multi-file test fixtures or mock dependency graphs. Use standard `unittest` without heavy mock frameworks if possible. Keep test files short and focused only on the most critical paths.
- **[TIER: MEDIUM] or [TIER: LARGE]**: You may write comprehensive tests with advanced fixtures, heavy mocking (e.g., `unittest.mock`), and deep integration testing.

---

## 3. The 3-Test Rule

For every distinct behavior described in the spec or `<done>` criteria, you MUST write exactly 3 tests minimum:

| Test | Description | Example |
|------|-------------|---------|
| **Happy Path** | The expected normal case | `assert login("user", "pass123") == SUCCESS` |
| **Boundary/Edge** | The value at or just past a limit | `assert login("user", "") == AuthError.EMPTY_PASSWORD` |
| **Adversarial** | "What subtle bug would this miss?" | `assert login("user", " ") == AuthError.EMPTY_PASSWORD` (whitespace-only) |

The Adversarial test must be written by asking: *"If the implementation had an off-by-one error, a type coercion bug, or handled only the exact case I tested — would this test catch it?"* If not, revise the test.

A test that passes with the correct implementation AND with the implementation deleted is not a valid test.

> [!CAUTION]
> **Adversarial Gate (MANDATORY before committing any test):**
> For every test you write, delete the implementation mentally (or actually comment it out
> and run). If the test still passes with no implementation, it is testing nothing.
> You MUST revise it until it fails with a deleted implementation.
> A test that cannot catch a deleted implementation is **forbidden** — do not commit it.

**[IF TIER: SMALL] Condensed 3-Test Rule:**
Write exactly 1 Happy Path test, 1 Edge Case test, and 1 Adversarial test per feature. The Adversarial test MUST fail if the implementation is deleted.

---

## 4. Static Analysis Gate

Before running any tests, you MUST run the project's static analysis tools. Tests do not count if static analysis fails.

Use the command appropriate to the project's language:

| Language | Command |
|----------|---------|
| Python | `mypy src/ && ruff check src/` |
| TypeScript/JS | `tsc --noEmit && eslint src/` |
| Go | `go vet ./...` |
| Other | Ask user for the project's lint/type command |

If no static analysis tool is configured, note it explicitly and continue — do not skip silently.

---

## 5. Integration Smoke Test

After unit tests pass, run one end-to-end test that exercises the feature as a real user would.

This test must:
- Start from the user-facing entry point (HTTP route, CLI command, UI action)
- Pass through the full stack (not just call the function in isolation)
- Assert the actual user-facing output, not an internal return value

The integration smoke test must be defined in the plan's `<done>` criteria. If it is not defined, ask the user to specify it before proceeding.

---

## 6. Visual Verification Protocol

**Triggered for any task that creates or modifies UI/frontend code.**

Check `.ai/MODEL_ENV.md` for the `mcp_tools.browser` value before choosing a path.

### Path A — Browser MCP Available (`browser: true`)

Execute these steps in order:

1. **Navigate**: Open the relevant route in the browser using `navigate_page`.
2. **Screenshot**: Capture the current state using `take_screenshot`. Describe what is visible versus what the spec requires.
3. **Network check**: Run `list_network_requests`. Assert zero 4xx or 5xx responses.
4. **Console check**: Run `get_console_message`. Assert zero JS errors or unhandled exceptions.
5. **Interaction**: Use `click`, `fill`, and `hover` to simulate the primary user flow. Take a screenshot after each critical state change.
6. **Lighthouse audit**: Run `lighthouse_audit`. Minimum passing scores:
   - Performance ≥ 80
   - Accessibility ≥ 90
   - SEO ≥ 80
   Any score below threshold is a blocking failure — treat it as a failing test.
7. **Human checkpoint**: Display the final screenshot and pause for user approval before marking the task complete.

### Path B — No Browser MCP (`browser: false`)

1. **CLI audit**: Run `npx lighthouse <url> --output json --chrome-flags="--headless"` if Node.js is available. Parse the JSON for the same score thresholds as Path A.
2. **Console errors via CLI**: Check `curl -s <url>` output for obvious structural errors.
3. **Human checkpoint** (mandatory): Set task type to `checkpoint:human-verify`. Instruct the user:
   > "Open <url> in your browser and confirm the following before I continue: [list what spec requires]"
   Wait for explicit user approval. Do not self-certify UI correctness without a human checkpoint when browser MCP is unavailable.

---

## Forbidden Test Patterns

Reject any test that matches these patterns — they will always pass regardless of implementation correctness:

| Anti-Pattern | Example | Why It's Invalid |
|---|---|---|
| Existence only | `assert result is not None` | Passes even if result is wrong |
| Always-true | `assert True` | Tests nothing |
| Mock tautology | `assert mock.called` | Tests that the mock was called, not that behavior is correct |
| Status-only HTTP | `assert response.status == 200` without checking body | A 200 with wrong data is a bug |
| Framework behavior | Testing that Flask returns 200 on a registered route | Tests the framework, not your logic |

---

## 6. Persistent Regression Suite

> [!IMPORTANT]
> Tests are not throwaway verification scripts. They are permanent project artifacts.
> Every task that writes or modifies a non-trivial function MUST leave a test behind.

### 6a. Where tests live

All tests live in a `tests/` directory that mirrors the `src/` structure:

```
src/
├── orchestrator.py     ←── tested by tests/test_orchestrator.py
└── rag.py              ←── tested by tests/test_rag.py
tests/
├── __init__.py         (empty — enables unittest discover)
├── test_orchestrator.py
└── test_rag.py
```

Use the project's established test runner. If none exists, use Python's
`unittest` (stdlib, zero new dependencies). Never add a test framework as a
dependency without explicit user approval.

### 6b. Lifecycle rules (MANDATORY)

Tests must stay coupled to their function for the entire lifetime of the code:

| Event | Required action |
|---|---|
| Function created | Write tests in the same commit |
| Function modified | Update its tests to reflect the new contract in the same commit |
| Function removed | Delete its tests in the same commit |
| Function renamed | Rename its tests to match in the same commit |

A test that covers a deleted or renamed function is a dead test. Dead tests
silently pass forever and give false confidence. They are forbidden.

### 6c. Regression baseline protocol

Before modifying any existing function:

1. **Locate** existing tests for that function in `tests/`
2. **Run them** and record the result (PASS/FAIL) before touching the code
3. **Implement** your change
4. **Run all tests** — existing + any new ones you wrote
5. If a previously-passing test now fails:
   - If the behavior change is **intentional**: update the test and add a comment
     explaining what changed and why (`# Behavior changed in Phase N: reason`)
   - If the behavior change is **unintentional**: you introduced a regression — fix it
     before marking the task complete

### 6d. API endpoint testing

For tasks that create or modify HTTP API endpoints, unit tests alone are not sufficient.
You MUST write an integration test that exercises the real HTTP layer:

```python
import urllib.request, urllib.error, json, subprocess, time, unittest

class TestMyEndpoint(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Start the real server as a subprocess
        cls.proc = subprocess.Popen(["python", "app.py"],
                                    stdout=subprocess.DEVNULL,
                                    stderr=subprocess.DEVNULL)
        time.sleep(1.5)  # wait for boot

    @classmethod
    def tearDownClass(cls):
        cls.proc.terminate()
        cls.proc.wait()

    def test_happy_path(self):
        req = urllib.request.urlopen("http://localhost:8000/api/resource")
        data = json.loads(req.read())
        self.assertEqual(req.status, 200)
        self.assertIn("expected_key", data)      # assert shape, not just status

    def test_invalid_input_returns_400(self):
        try:
            urllib.request.urlopen("http://localhost:8000/api/resource?id=INVALID")
            self.fail("Expected HTTP 400, got 200")
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 400)
```

Rules for API tests:
- Always assert the **response body**, not just the status code
- Always include at least one **error/rejection case** (4xx response)
- Use a real server started in `setUpClass` — do not mock the HTTP layer
- The server must be terminated in `tearDownClass` even if tests fail

### 6e. What tests cannot verify — human checkpoint rule

Some correctness cannot be automated. When a task produces output that requires
human judgment, the agent MUST NOT self-certify. Instead, it must:

1. Complete all automated tests that can be written
2. Output a clear, non-blocking note:

> **⚠️ MANUAL VERIFICATION REQUIRED**
> Automated tests cannot verify: [specific thing — visual layout, design quality,
> subjective correctness of generated text, etc.]
> Please review [screenshot / rendered output / file] and confirm before proceeding.

The task is marked complete after this note is output. The human reviews asynchronously.
This applies to: UI visual quality, design aesthetics, LLM-generated content correctness,
audio/video output, and any output that requires subjective human judgment.
