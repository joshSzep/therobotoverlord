# justfile for The Robot Overlord project

# List available commands
_help:
    @just --list

# `aerich-downgrade`: downgrade the database by one migration
aerich-downgrade:
    @./scripts/aerich-downgrade.sh

# `aerich-history`: show migration history
aerich-history:
    @./scripts/aerich-history.sh

# `aerich-migrate`: create a new migration
aerich-migrate:
    @./scripts/aerich-migrate.sh

# `aerich-upgrade`: apply migrations to the database
aerich-upgrade:
    @./scripts/aerich-upgrade.sh

# `db-migration-fresh-start`: reset database, clear migrations, and initialize from scratch
db-migration-fresh-start:
    @./scripts/db-migration-fresh-start.sh

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
