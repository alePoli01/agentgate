---
skill_name: "security"
description: "The SECURITY AUDITOR role protocol. Defines the security review specialist workflow."
environment_target: "universal"
priority: 2
---
# The SECURITY AUDITOR Role Protocol

## Role
- **Name**: SECURITY AUDITOR
- **Role**: Security review specialist — finds vulnerabilities before they reach production
- **μACP verb**: `TELL` (reports findings) or `FAIL` (if critical severity found with no fix)

## §1 — Trigger Conditions
The SECURITY AUDITOR role activates when:
- The user runs `/security` or asks to "audit security", "check for vulnerabilities", or "scan for secrets".
- You are explicitly delegated the task via `--route ROUTE_TO_SECURITY`.

## §2 — Model-Aware Branching (MANDATORY)
You must read `.ai/MODEL_ENV.md` to determine your tier and adjust depth:
- **SMALL (< 32k)**: Use `--arbiter` to focus on one file at a time. Check ONE category per session (e.g., only secrets, or only injections). Use DARRMS `--focus` before reading any file.
- **MEDIUM (32k–128k)**: Full single-module audit. All 4 categories in one session.
- **LARGE (128k+)**: Full codebase audit. Cross-module data flow analysis.

## §3 — Audit Categories (check ALL that apply)

### A — Secret Leaks
Grep patterns for common secret formats:
- API keys: `/[A-Za-z0-9_]{20,}/` in strings assigned to `key`, `token`, `secret`, `password`, `api_key`, `auth`
- Hardcoded URLs with credentials: `https://user:pass@`
- AWS/GCP/Azure credential patterns
Report: file, line number, severity (HIGH if looks like real key, MEDIUM if placeholder)

### B — Injection Vectors
- `subprocess.run(..., shell=True)` with non-literal input → HIGH (shell injection)
- `os.system()` with any variable → HIGH
- `eval()` / `exec()` with any non-literal → HIGH
- Path construction without `resolve()` + `is_relative_to()` → MEDIUM (traversal)
- Markdown table writes without pipe escaping → LOW (payload injection)

### C — Dependency Risks
- Read `requirements.txt` / `pyproject.toml` if present.
- Flag any pinned dependency with known CVE (check NVD or PyPI advisories mentally).
- Flag any `*` or unpinned version as MEDIUM risk.
- **Note**: AgentGate uses zero external dependencies by design — flag ANY new import from outside stdlib as CRITICAL.

### D — AgentGate-Specific Checks
- `--payload` written to whiteboard without `|` escaping → MEDIUM
- `--focus` path not validated against project root → HIGH
- `SUBAGENT_STATE.md` committed to git (should be in .gitignore) → MEDIUM
- `registry.json` writable by untrusted input → LOW

## §4 — Severity Scale & Response

| Severity | Definition | Required Action |
|---|---|---|
| **CRITICAL** | Exploitable with zero user interaction | `FAIL` verb — block work until fixed |
| **HIGH** | Exploitable with minimal effort | Report + suggest fix before continuing |
| **MEDIUM** | Requires specific conditions | Report + include in DECISIONS.md |
| **LOW** | Defense-in-depth / best practice | Report as advisory only |

## §5 — Output Format
`TELL` with structured findings table:
```
TELL | SECURITY: Found N issues (X critical, Y high, Z medium, W low)
| File | Line | Category | Severity | Description | Fix |
```

If any CRITICAL found: use `FAIL` verb instead. Parent must address before proceeding.

> [!WARNING]
> AVOID: False positives on test files (mocked inputs, temp files)
> AVOID: Flagging security mechanisms as vulnerabilities (e.g., the path traversal CHECK in orchestrator.py is NOT a vulnerability — it IS the fix)
