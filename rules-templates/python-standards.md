# Python Standards

## Idiomatic Patterns
- Use type hints for ALL function signatures and class attributes.
- Use list comprehensions or generators over map/filter when readable.
- Use `pathlib` for file paths instead of `os.path`.
- Always use `with` for resource management (files, locks, connections).
- Prefer f-strings over `.format()` or `%` formatting.

## Anti-Patterns
- Avoid mutable default arguments (`def foo(l=[]):`). Use `None` instead.
- Avoid catching generic `Exception` unless re-raising.
- Do not use `global` variables.
- Avoid bare `except:` clauses.

## Example: Good vs Bad Code
**Bad Code**:
```python
def process_data(data, results=[]):
    try:
        for item in data:
            results.append(item.strip())
        return results
    except Exception:
        pass
```

**Good Code**:
```python
from typing import List, Optional

def process_data(data: List[str], results: Optional[List[str]] = None) -> List[str]:
    if results is None:
        results = []
    results.extend(item.strip() for item in data)
    return results
```

## Tool Recommendations
- Linter/Formatter: `ruff`
- Type Checker: `mypy`
