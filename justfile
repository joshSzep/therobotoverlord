# justfile for The Robot Overlord project

# List available commands
default:
    @just --list

# Run the setup script to install dependencies
setup:
    @./scripts/setup.sh

# Verify pre-commit hooks are installed and pass
verify:
    @./scripts/verify.sh
