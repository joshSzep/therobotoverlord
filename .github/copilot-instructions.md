# The Robot Overlord Project Guidelines

RULE #1: **DO NOT** add docstrings unless specifically requested.

## Project Vision
- **Concept**: AI-moderated debate platform with satirical Soviet propaganda aesthetic
- **Core Flow**: Users submit posts → AI analysis → APPROVE (post appears) or REJECT (tombstone counter)
- **Theme**: Authoritarian robot overlord ("CITIZEN, YOUR LOGIC REQUIRES CALIBRATION")
- **Tech Stack**: FastAPI+Tortoise ORM backend, Next.js frontend, PostgreSQL, OpenAI/Anthropic APIs
- **Key Features**: User accounts with approval/rejection counters, threaded debates, AI moderation pipeline, Soviet-themed UI

## Project Structure
- `backend/`: FastAPI backend (Python)
  - `migrations/`: Tortoise ORM/aerich migrations
  - `src/backend/`: Source code
    - `app.py`: FastAPI application setup
    - `db/`: Database configuration
      - `config.py`: Tortoise ORM/aerich configuration
      - `base.py`: Base model for all database models
      - `models/`: Database models, 1 model per file
    - `routes/`: API endpoints by feature, one package per feature
    - `tasks/`: Background tasks
    - `utils/`: Shared utilities
  - `tests/`: Test files (mirrors source code directory structure)
  - `pyproject.toml`: Project configuration
- `frontend/`: Next.js frontend (TypeScript)
- `scripts/`: Shell scripts for workflows
- `plans/`: Markdown files for LLM consumption (technical design documentation)
- `plans/checklists/`: Markdown files for LLM consumption (checklists)
- `justfile`: Command runner
- `LLM_RULES.md`: Central location for AI assistant guidelines
- `.github/workflows/`: CI/CD configuration

### Routes organized by feature
The backend routes follow a feature-based modular structure, for example:
```
src/backend/
├── app.py             # FastAPI application setup
└── routes/            # API endpoints by feature
    └── health/        # Example feature module
        ├── __init__.py     # Router setup
        ├── check.py        # REST endpoint
        ├── heartbeat.py    # WebSocket endpoint
        ├── schemas.py      # Pydantic schemas
        └── utils.py        # Feature utilities
```

**Key principles**:
- Routes organized by feature with separation of concerns (endpoints, schemas, utilities)
- Each feature has consistent module naming (`__init__.py`, `schemas.py`, `utils.py`)
- **RULE #2: ONE ROUTE PER FILE** - Each API endpoint must be in its own file. For example, `list_posts`, `create_post`, `get_post`, etc. should each be in separate files named accordingly
- **RULE #3: DESCRIPTIVE ROUTE FILENAMES** - Route filenames must match the function name they contain (e.g., `list_posts.py`, `create_post.py`, `get_post.py`) to ensure clarity and discoverability

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

- **Database Migration Commands**:
  - `just aerich-downgrade`: Revert the most recent migration
  - `just aerich-history`: Show migration history
  - `just aerich-migrate`: Create a new migration after model changes
  - `just aerich-upgrade`: Apply pending migrations to the database

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
    return result
```

### Documentation & Testing
- Avoid writing any docstrings at all.
- **NEVER** add a docstring to the top of a python file unless specifically requested.
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

## MOST IMPORTANTLY: Docstring etiquette

- Docstrings should only be added to functions; not modules!
- If a module needs documentation that would be a sign that it **needs to be broken up into smaller modules**.
- If you put a docstring on a module we will have to keep it up to date which is a waste of time and often is forgotten which leads to confusion.
- This is an application, not a library for external consumption, being built largely by you, the AI assistant.
- Even in functions, docstrings should only exist if they explain something that cannot be explained by the function definition, parameters, and return type.

BAD EXAMPLE (Docstring adds no value):
```python
def check() -> HealthCheckResponse:
    """Simple health check endpoint."""
    return build_health_check_response()
```

GOOD EXAMPLE:
```python
def check() -> HealthCheckResponse:
    return build_health_check_response()
```

BAD EXAMPLE (Docstring adds only liability):
```python
def echo_if_hello(well_named_param: str) -> Optional[str]:
    """
    Simple function that returns a string if the param is "hello".

    Args:
        well_named_param: The param to check.

    Returns:
        Optional[str]: The string "hello" if the param is "hello", otherwise None.
    """
    if well_named_param == "hello":
        return "hello"
    return None
```

GOOD EXAMPLE (Docstring adds value) located in our app's `backend.utils.datetime` module:
```python
from datetime import UTC
from datetime import datetime


def now_utc() -> datetime:
    """
    ALWAYS use this and NEVER use datetime.now() or datetime.utcnow() directly,
    as they are not timezone aware.
    """
    return datetime.now(tz=UTC)

```

## Criteria for Keeping a Docstring

A docstring should **ONLY** be kept if it meets any of the following criteria:
- It explains complex logic that cannot be understood from the function signature alone
- It documents non-obvious side effects or behaviors
- It provides critical context that would be lost if removed
- It cannot be replaced by better naming or type annotations
