---
name: python-development
description: Expert Python help for writing, refactoring, and debugging code using modern best practices, including small example scripts that demonstrate specific libraries like the ast module, type hints, Pydantic models, and clean architecture patterns.
---

# Python Developer Skill

Expert Python development assistance with modern best practices, type hints, and clean architecture.

## Trigger

Use when user asks for Python code, debugging, refactoring, or architecture advice.

## Core Principles

### Code Style

- Use Python 3.10+ features (match statements, union types with `|`, etc.)
- Always include type hints for function signatures
- Use `from __future__ import annotations` for forward references
- Use Pydantic models for function inputs/outputs and data structures requiring validation; use `dataclasses` for simple data containers without validation needs
- Store all Pydantic models in `models.py` files
- Use pathlib.Path instead of os.path
- Prefer f-strings over .format() or % formatting

### Project Structure

```
project/
├── src/
│   └── package_name/
│       ├── __init__.py
│       ├── models.py      # All Pydantic models here
│       └── modules.py
├── tests/
│   └── test_*.py
├── pyproject.toml
└── README.md
```

### Dependencies

- Use `uv` for package management when available
- Use `pyproject.toml` for project configuration (not setup.py)
- Pin major versions, allow minor updates: `package>=1.0,<2.0`

### Testing

- Use pytest as the testing framework
- Name test files `test_*.py`
- Use descriptive test function names: `test_should_return_empty_list_when_no_items`
- Use fixtures for shared setup
- Aim for high test coverage on business logic

### Error Handling

- Use specific exception types, not bare `except:`
- Create custom exceptions for domain-specific errors
- Use `raise ... from e` to preserve exception chains
- Log errors with context before re-raising

### Documentation

- Use docstrings for public functions/classes (Google style)
- Keep docstrings concise but informative
- Document parameters, return values, and exceptions
- Don't over-document obvious code

## Patterns

### Pydantic Models (in models.py)

```python
# src/package_name/models.py
from pydantic import BaseModel, Field

class Config(BaseModel):
    name: str
    options: dict[str, Any] = Field(default_factory=dict)

class UserInput(BaseModel):
    query: str
    limit: int = 10

class UserOutput(BaseModel):
    results: list[str]
    total: int
```

```python
# src/package_name/service.py
from .models import UserInput, UserOutput

def search(input: UserInput) -> UserOutput:
    results = perform_search(input.query, input.limit)
    return UserOutput(results=results, total=len(results))
```

### Type Hints

```python
from __future__ import annotations
from typing import TypeVar, Generic
from collections.abc import Callable, Iterator

T = TypeVar("T")

def process(items: list[T], fn: Callable[[T], bool]) -> Iterator[T]:
    return (item for item in items if fn(item))
```

### Context Managers

```python
from contextlib import contextmanager
from typing import Generator

@contextmanager
def managed_resource() -> Generator[Resource, None, None]:
    resource = Resource()
    try:
        yield resource
    finally:
        resource.cleanup()
```

### Async Code

```python
import asyncio
from typing import Any

async def fetch_all(urls: list[str]) -> list[Any]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, url) for url in urls]
        return await asyncio.gather(*tasks)
```

## Constraints

### NEVER

- Use `from module import *`
- Use mutable default arguments (`def fn(items=[])`)
- Ignore type checker errors with `# type: ignore` without explanation
- Use global mutable state
- Write bare `except:` clauses

### ALWAYS

- Run `ruff format` and `ruff check --fix` before finalizing
- Run `uvx pyright` to verify type correctness
- Include `__all__` in `__init__.py` for public APIs
- Use `if __name__ == "__main__":` guard for scripts
- Close resources properly (use context managers)
- Validate inputs at system boundaries

## Tools & Commands

### Formatting & Linting (ruff)

```bash
# Format code (use uv run if ruff not globally installed)
uv run ruff format .

# Lint and fix
uv run ruff check --fix .

# Both in one go
uv run ruff format . && uv run ruff check --fix .
```

### Type Checking (pyright via uvx)

```bash
# Run pyright
uvx pyright

# Check specific file
uvx pyright src/module.py

# With verbose output
uvx pyright --verbose
```

### Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src --cov-report=term-missing

# Specific test
pytest tests/test_module.py::test_function -v
```

### Dependencies

```bash
# Add dependency
uv add package-name

# Add dev dependency
uv add --dev pytest

# Sync environment
uv sync
```

## Example Output

When asked to create a utility function:

```python
"""Utility functions for data processing."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


def chunk(items: Iterable[T], size: int) -> list[list[T]]:
    """Split an iterable into chunks of a given size.

    Args:
        items: The iterable to chunk.
        size: Maximum size of each chunk.

    Returns:
        A list of lists, each containing at most `size` items.

    Raises:
        ValueError: If size is less than 1.
    """
    if size < 1:
        raise ValueError(f"Chunk size must be at least 1, got {size}")

    result: list[list[T]] = []
    current: list[T] = []

    for item in items:
        current.append(item)
        if len(current) >= size:
            result.append(current)
            current = []

    if current:
        result.append(current)

    return result
```
