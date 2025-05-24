# justfile for The Robot Overlord project

# List available commands
default:
    @just --list

# Do a `git add .` from the root directory
git-add-all:
    @git add .

# Do a `git restore .` from the root directory
git-restore-all:
    @git restore .

# Do a `git restore --staged .` from the root directory
git-restore-staged-all:
    @git restore --staged .

# Show `git status` from the root directory
git-status:
    @git status

# Run pre-commit hooks (format, lint, test)
pre-commit:
    @./scripts/pre-commit.sh

# Run the setup script
setup:
    @./scripts/setup.sh

# Run tests with coverage
test:
    @./scripts/test.sh
