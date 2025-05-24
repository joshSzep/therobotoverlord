# justfile for The Robot Overlord project

# `DEFAULT`: List available commands
default:
    @just --list

# `eslint`: lint the frontend
eslint:
    @./scripts/eslint.sh

# `gunicorn`: serve the backend in PRODUCTION
gunicorn:
    @./scripts/gunicorn.sh

# `mypy`: type check the backend (reference implementation)
mypy:
    @./scripts/mypy.sh

# `pre-commit`: run format, lint, and test on all files
pre-commit:
    @./scripts/pre-commit.sh

# `pyright`: type check the backend (microsoft implementation)
pyright:
    @./scripts/pyright.sh

# `pytest`: test the backend
pytest:
    @./scripts/pytest.sh

# `ruff check`: lint the backend
ruff-check:
    @./scripts/ruff-check.sh

# `ruff format`: format the backend
ruff-format:
    @./scripts/ruff-format.sh

# `setup`: install dependencies and pre-commit hooks
setup:
    @./scripts/setup.sh

# `uvicorn`: serve the backend in DEVELOPMENT
uvicorn:
    @./scripts/uvicorn.sh

# `update-llm-rules`: update all LLM rule files from LLM_RULES.md
update-llm-rules:
    @./scripts/update-llm-rules.sh
