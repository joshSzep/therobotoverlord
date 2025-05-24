# justfile for The Robot Overlord project

# List available commands
default:
    @just --list

# Run the setup script
setup:
    @./scripts/setup.sh

# Run pre-commit hooks (format, lint, test)
pre-commit:
    @./scripts/pre-commit.sh

# Run tests with coverage
test:
    @./scripts/test.sh
