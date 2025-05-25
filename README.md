# therobotoverlord

[![Backend Checks](https://github.com/joshSzep/therobotoverlord/actions/workflows/backend-checks.yml/badge.svg)](https://github.com/joshSzep/therobotoverlord/actions/workflows/backend-checks.yml)
[![Frontend Checks](https://github.com/joshSzep/therobotoverlord/actions/workflows/frontend-checks.yml/badge.svg)](https://github.com/joshSzep/therobotoverlord/actions/workflows/frontend-checks.yml)
[![Global Checks](https://github.com/joshSzep/therobotoverlord/actions/workflows/global-checks.yml/badge.svg)](https://github.com/joshSzep/therobotoverlord/actions/workflows/global-checks.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Coverage](https://img.shields.io/badge/coverage-100%25-brightgreen)](https://github.com/joshSzep/therobotoverlord)


I FOR ONE WELCOME **THE ROBOT OVERLORD**

## Pre-requisites

- `git` - [Version Control System](https://git-scm.com/)
- `just` - [Command Runner](https://just.systems/)
- `node` - [JavaScript Runtime and Package Manager](https://nodejs.org/)
- `uv` - [Python Package Manager](https://github.com/urbit/uv)
- `python` - [Python Runtime](https://www.python.org/)

## Quick Start

1. Clone the repository.
2. Run `just setup` to install dependencies.
3. Run `just pre-commit` to verify the project (this will run format, lint, and test)

## Monorepo Structure

It's important to know the following about the monorepo structure:

- `backend/`: [FastAPI backend](./backend/README.md).
- `frontend/`: [Next.js frontend](./frontend/README.md).
- `scripts/`: [Scripts](./scripts/README.md) - used for managing the monorepo.
- `justfile`: [Justfile](./justfile) - used for executing commands in the monorepo.
