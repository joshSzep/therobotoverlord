# therobotoverlord

[![Backend Checks](https://github.com/joshSzep/therobotoverlord/actions/workflows/backend-checks.yml/badge.svg)](https://github.com/joshSzep/therobotoverlord/actions/workflows/backend-checks.yml)
[![Frontend Checks](https://github.com/joshSzep/therobotoverlord/actions/workflows/frontend-checks.yml/badge.svg)](https://github.com/joshSzep/therobotoverlord/actions/workflows/frontend-checks.yml)
[![Global Checks](https://github.com/joshSzep/therobotoverlord/actions/workflows/global-checks.yml/badge.svg)](https://github.com/joshSzep/therobotoverlord/actions/workflows/global-checks.yml)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![Deploy](https://render.com/api/v1/services/srv-d0u3f5be5dus738jr9h0/deploys/latest/badge)](https://render.com)


I FOR ONE WELCOME [**THE ROBOT OVERLORD**](https://therobotoverlord.com)

## Project Overview

A debate platform with a unique twist: it's moderated by a single AI "robot overlord" with a tongue-in-cheek Soviet propaganda aesthetic.

### Core Concept
- Users submit posts/replies to threaded debate topics
- Every submission goes through AI analysis before appearing
- AI either APPROVES (post appears) or REJECTS (becomes a "tombstone" - permanent shame counter)
- Theme: Satirical Soviet authoritarianism
- Visual style: Retro-Soviet industrial propaganda with robot mascot
- UX voice: Authoritarian but helpful ("CITIZEN, YOUR LOGIC REQUIRES CALIBRATION")

### Tech Stack
- **Backend**: FastAPI + Tortoise ORM (Django-like ORM with async support)
- **Frontend**: Next.js (React SPA)
- **Database**: PostgreSQL
- **Deployment**: Backend on Render, Frontend on Vercel
- **AI**: OpenAI/Anthropic APIs for content moderation

### Key Features
1. User accounts with approval/rejection counters (checkmarks vs tombstones)
2. Threaded debate topics (Reddit/HN style)
3. AI moderation pipeline for pre-publication analysis
4. Binary AI decisions with feedback
5. Soviet-themed UI with dramatic loading states
6. Click-and-wait judgment flow

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
- `plans/`: Markdown files intended for LLM consumption - serves as technical design documentation for AI-assisted development.
