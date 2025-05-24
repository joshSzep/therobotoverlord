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

# Show `git status` from the root directory
git-status:
    @git status

# Do a `git add .` from the root directory
git-add-all:
    @git add .

# Do a `git restore .` from the root directory
git-restore-all:
    @git restore .

# Do a `git restore --staged .` from the root directory
git-restore-staged-all:
    @git restore --staged .
