You are helping build an MVP for a debate platform with a unique twist: it's moderated by a single AI "robot overlord" with a tongue-in-cheek Soviet propaganda aesthetic.

CORE CONCEPT:
- Users submit posts/replies to threaded debate topics
- Every submission goes through AI analysis before appearing
- AI either APPROVES (post appears) or REJECTS (becomes a "tombstone" - permanent shame counter)
- The theme is satirical Soviet authoritarianism: "iforonewelcomeournewrobotoverlord.com"
- Visual style: retro-Soviet industrial propaganda with robot mascot
- UX voice: authoritarian but helpful ("CITIZEN, YOUR LOGIC REQUIRES CALIBRATION")

TECH STACK DECISIONS MADE:
- Backend: FastAPI + Tortoise ORM (Django-like ORM syntax with async support)
- Frontend: Next.js (React SPA for smooth "waiting for judgment" UX)
- Database: PostgreSQL
- Deployment: Backend on Render, Frontend on Vercel
- AI: OpenAI/Anthropic APIs for content moderation

KEY FEATURES FOR MVP:
1. User accounts with approval/rejection counters (checkmarks vs tombstones)
2. Threaded debate topics (Reddit/HN style)
3. AI moderation pipeline - every post analyzed before publication
4. Binary AI decisions: APPROVED or REJECTED with feedback
5. Soviet-themed UI with dramatic loading states during AI processing
6. No real-time features - click and wait for judgment

DATABASE SCHEMA: Already designed in DBML with tables for users, topics, posts, ai_analyses, rejections, etc. Rejection tracking is key for "tombstone" shame counters.

CRITICAL UX FLOW:
Submit post → "THE OVERLORD DELIBERATES..." loading → Dramatic reveal of approval/rejection → Either post appears in thread OR user sees rejection reason + tombstone count increases

The human is an experienced Python engineer who's organized, great at AI prompting, but new to React/frontend. They want to build this solo using AI assistance for design/frontend work.

What aspect of this project do you want to work on?
