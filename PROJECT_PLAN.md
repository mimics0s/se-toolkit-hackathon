# ExcuseForge — Project Plan

## Project Idea (for TA approval — Task 2)

### End-user
IT university students in the SET course who failed to submit lab tasks on time (Thursday 23:59 deadline) and need a plausible technical reason to explain to their TA.

### Problem
Students spend 30+ minutes panicking and inventing fake technical excuses. Most sound fake ("my cat walked on keyboard") and TAs don't buy them. Students need something quick, believable, and technically accurate.

### Product idea (one sentence)
ExcuseForge generates realistic, technically-sounding excuses tailored to the university VM environment in one click — no prompt writing needed.

### Core feature
**One-click excuse generation** — click a button, get a believable, course-specific technical excuse (e.g., "Docker build cache corrupted due to Ubuntu 24.04 kernel update on university VM") that the student can copy and paste into Moodle/chat.

---

## Version 1 Plan (shown to TA during lab)

**Scope:** One core feature that works end-to-end — generate and save an excuse.

### Components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Backend | Python + FastAPI | REST API for excuse generation |
| Database | SQLite (V1) → PostgreSQL (V2) | Store generated excuses with timestamps |
| Web client | HTML/CSS/JS (vanilla, single page) | Button to generate, display result, copy to clipboard |

### Core feature flow
1. User opens web app
2. Clicks "Generate Excuse"
3. Backend picks from a curated bank of realistic technical scenarios, combines them into a unique excuse
4. Excuse is displayed on the page with a "Copy" button
5. Excuse is logged to the database with timestamp

### Excuse generation logic
- Uses a **template-based approach** with randomized components:
  - **Cause:** kernel update, Docker cache corruption, VM snapshot rollback, network partition, disk quota exceeded, systemd service crash
  - **Context:** university VM, Moodle upload, lab submission portal, Docker container
  - **Symptom:** build failed, timeout, connection refused, permission denied
  - **Course-specific details:** Thursday deadline, VM Telegram blocks, Ubuntu 24.04, TA submission system

### Deliverable for TA
- Working web app: open URL → click button → get excuse → copy it
- TA tries it and gives feedback

---

## Version 2 Plan (deployed by deadline)

**Scope:** Improve V1 based on TA feedback + add voting, history, per-lab filter, Docker deployment.

### New features
| Feature | Description |
|---------|-------------|
| 👍/👎 Voting | User can vote on each generated excuse to track which ones work best |
| History | Shows all previously generated excuses with timestamps and vote counts |
| Per-lab filter | Filter history by lab number (Lab 1, Lab 2, etc.) |
| Docker deployment | All services (backend + DB + web client) containerized via Docker Compose |

### Architecture
```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Web Client │────▶│  FastAPI     │────▶│  PostgreSQL │
│  (HTML/JS)  │     │  Backend     │     │  Database   │
└─────────────┘     └──────────────┘     └─────────────┘
       │                   │
       │  Display excuse   │  Generate excuse
       │  + history        │  + save to DB
       └───────────────────┘
```

### Deployment
- **OS:** Ubuntu 24.04 (same as university VMs)
- **Method:** Docker Compose (backend + PostgreSQL + nginx for static files)
- **Access:** HTTP on port 8000 (or reverse proxy via nginx)

---

## What makes this different from a generic LLM?

| Aspect | DeepSeek / ChatGPT | ExcuseForge |
|--------|--------------------|-------------|
| Speed | 10-30s (type prompt, wait) | 1 second (one click) |
| Effort | Write prompt, refine | Zero typing |
| Context | Generic | Course-specific (SET, Thursday deadline, VM details) |
| History | None | Built-in, filterable by lab |
| Feedback | None | Community voting (👍/👎) |
