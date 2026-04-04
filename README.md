# ExcuseForge

One-click realistic, technically-sounding excuse generator for university students who missed lab deadlines.

## Demo

*(Screenshots will be added after Version 1 implementation)*

## Product Context

### End users
IT university students in the SET course who missed the Thursday 23:59 lab submission deadline.

### Problem
Students waste 30+ minutes inventing fake technical excuses that often sound fake and aren't convincing to TAs.

### Solution
ExcuseForge generates course-specific, technically plausible excuses in 1 second with a single click — no prompt writing needed. Includes history tracking and community voting to identify the most believable excuses.

## Features

### Implemented
- [ ] One-click excuse generation
- [ ] Course-specific technical scenarios (Ubuntu 24.04, Docker, VM environment)
- [ ] Copy to clipboard
- [ ] REST API backend
- [ ] Database logging

### Not yet implemented (Version 2)
- [ ] 👍/👎 voting on excuses
- [ ] Excuse history with timestamps
- [ ] Per-lab filtering
- [ ] Docker Compose deployment
- [ ] PostgreSQL migration

## Usage

1. Open the web app in your browser
2. Click **"Generate Excuse"**
3. Read the generated excuse
4. Click **"Copy"** to copy to clipboard
5. Paste into Moodle/chat for your TA

### Example output
> "During the final build for Lab 7 submission, the Docker build cache became corrupted after the university VM's Ubuntu 24.04 kernel update. The `systemd-resolved` service entered a restart loop, causing DNS resolution to fail for the Moodle upload endpoint. Attempted `docker system prune --all` but the VM's disk quota was already exceeded at 98% usage."

## Deployment

### Requirements
- Ubuntu 24.04 VM
- Docker and Docker Compose installed
- Port 8000 available

### Step-by-step

**Version 1 (local development):**
```bash
# Clone the repository
git clone <repo-url>
cd se-toolkit-hackathon

# Install dependencies
pip install -r requirements.txt

# Start the backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Open in browser
# http://localhost:8000
```

**Version 2 (Docker deployment):**
```bash
# Build and start all services
docker compose up -d

# Access at:
# http://<vm-ip>:8000
```

### Architecture
```
Web Client (HTML/JS) → FastAPI Backend → PostgreSQL Database
```
