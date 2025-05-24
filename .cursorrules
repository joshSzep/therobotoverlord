# The Robot Overlord Project Guidelines

## Project Structure
- `backend/`: FastAPI backend (Python)
  - `src/backend/`: Source code
  - `tests/`: Test files (mirrors source code directory structure)
- `frontend/`: Next.js frontend (TypeScript)
- `scripts/`: Shell scripts for workflows
- `justfile`: Command runner
- `LLM_RULES.md`: Central location for AI assistant guidelines
- `.github/workflows/`: CI/CD configuration

### Backend Organization
The backend follows a feature-based modular structure:
```
src/backend/
├── app.py             # FastAPI application setup
├── routes/            # API endpoints by feature
│   └── health/        # Example feature module
│       ├── __init__.py     # Router setup
│       ├── check.py        # REST endpoint
│       ├── heartbeat.py    # WebSocket endpoint
│       ├── models.py       # Pydantic models
│       └── utils.py        # Feature utilities
└── utils/             # Shared utilities
```

**Key principles**: Routes organized by feature with separation of concerns (endpoints, models, utilities). Each feature has consistent module naming (`__init__.py`, `models.py`, `utils.py`). Common functionality in `utils/`.

## Development
- **Prerequisites**: `git`, `just`, `node`, `uv`, `python` (3.12.10)
- **Key Commands**:
  - `just setup`: Install dependencies
  - `just pre-commit`: Format, lint, test
  - `just uvicorn`: Serve backend in development mode
  - `just gunicorn`: Serve backend in production mode
  - `just ruff-format`: Format backend code
  - `just ruff-check`: Lint backend code
  - `just mypy`: Type check backend (reference implementation)
  - `just pyright`: Type check backend (Microsoft implementation)
  - `just pytest`: Test backend (runs all tests with coverage)
  - `just eslint`: Lint frontend
  - `just update-llm-rules`: Update all AI assistant rule files from LLM_RULES.md

- **Running Specific Tests**:
  - From project root: `cd backend && uv run pytest tests/path/to/test_file.py`
  - If already in backend dir: `uv run pytest tests/path/to/test_file.py`
  - Run specific test function: `uv run pytest tests/path/to/test_file.py::test_function_name`

## Python Coding Style

**General principle**: When in doubt, follow PEP 8.

### Code Organization
- **Imports**: Group by source (stdlib → third-party → project), alphabetize, one per line, absolute imports ONLY. NEVER use relative imports. Here is an example, except DO NOT literally use these comments in your code (they are for illustration purposes only):
```python
# Standard library imports
import asyncio
from datetime import datetime

# Third-party imports
from fastapi import APIRouter

# Project-specific imports
from backend.utils.datetime import now
```

- **Formatting**: 88 char line limit, 4 spaces indent, double quotes, two blank lines before top-level definitions
- **Functions**: Type annotations required, trailing commas in multi-line params
```python
async def example(
    param: str,
) -> ReturnType:
    """Concise docstring explaining purpose."""
    return result
```

### Documentation & Testing
- Docstrings for all functions using triple double quotes
- Tests follow Arrange-Act-Assert pattern with 100% coverage required
- Code quality enforced via Ruff (rules: E, F, I, UP, N, B, A, C4, RET, SIM, ERA), Mypy, Pyright, and pre-commit hooks

### Error Handling
- Prefer using exceptions for error handling
- NEVER overload return types (e.g., don't use `Optional[<type>]` with `None` to signal errors)
- Raise specific exceptions rather than generic ones
- Handle exceptions at appropriate levels of abstraction

## Async Programming
- **All API endpoints MUST be async** (`async def`)
- Use async libraries for I/O operations (`asyncio`, async DB clients, `httpx`)
- Avoid blocking operations in async functions
```python
# CORRECT - Always use async for endpoints
async def check() -> HealthCheckResponse:
    """Simple health check endpoint."""
    return build_health_check_response()
```

## Frontend & CI/CD
- **Frontend**: TypeScript, ESLint, Next.js conventions, TailwindCSS
- **CI/CD**: GitHub Actions for code quality on push/PR
