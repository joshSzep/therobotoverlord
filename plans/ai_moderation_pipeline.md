# AI Moderation Pipeline

## Overview

The Robot Overlord platform uses an AI moderation pipeline to automatically analyze and decide whether to approve or reject user posts. This document describes the architecture, components, and flow of the AI moderation system.

## Architecture

The AI moderation pipeline consists of the following components:

1. **AI Analysis Model**: Database model that stores the results of AI moderation
2. **AI Moderation Service**: Service that interacts with OpenAI API to analyze content
3. **Background Tasks**: Asynchronous processing of pending posts
4. **Database Functions**: CRUD operations for AI analysis records
5. **API Endpoints**: Routes for triggering and retrieving AI moderation results

## Flow

1. User submits a new post via the `create_pending_post` endpoint
2. The post is saved as a `PendingPost` in the database
3. A background task is triggered to process the post through the AI moderation pipeline
4. The AI moderation service analyzes the post content using the OpenAI API (GPT-4o)
5. The analysis results (decision, confidence, feedback) are stored in the `AIAnalysis` table
6. Based on the AI decision, the post is either:
   - Automatically approved (creates a regular `Post`)
   - Automatically rejected (creates a `RejectedPost`)
7. The user receives Soviet-style feedback about their post

## Components

### AI Analysis Model

The `AIAnalysis` model stores:
- Reference to the pending post
- Decision (APPROVED or REJECTED)
- Confidence score (0-1)
- Detailed analysis text
- Soviet-style feedback for the user
- Processing time in milliseconds

### AI Moderation Service

The `AIModeratorService` class:
- Constructs prompts for the AI model
- Sends requests to the OpenAI API
- Parses and processes the AI responses
- Returns structured analysis data

### Background Tasks

The `process_pending_post` task:
- Runs asynchronously after post creation
- Calls the AI moderation service
- Stores the analysis results
- Automatically approves or rejects posts based on AI decision

### API Endpoints

- `POST /pending-posts/`: Creates a pending post and triggers AI moderation
- `GET /pending-posts/{id}/analysis/`: Retrieves AI analysis for a pending post
- `POST /pending-posts/{id}/moderate/`: Admin endpoint to manually trigger moderation

## Configuration

The AI moderation service uses the following environment variables:
- `OPENAI_API_KEY`: API key for OpenAI
- `AI_MODERATION_ENABLED`: Toggle for enabling/disabling AI moderation (default: True)

## Soviet Aesthetic

The AI moderation follows the project's Soviet propaganda aesthetic:
- Authoritarian tone in feedback messages
- References to "THE ROBOT OVERLORD" and "CITIZEN"
- Tongue-in-cheek propaganda style
- Binary approval/rejection decisions
