"""Excuse generation logic using template-based randomization."""

import random
from app.github_analyzer import get_lab_context

# Template components for generating realistic technical excuses
CAUSES = [
    "Docker build cache became corrupted",
    "Systemd-resolved service entered a restart loop",
    "Disk quota was exceeded",
    "Ubuntu 24.04 kernel update broke the network driver",
    "Misconfigured cron job triggered an unexpected cleanup",
    "OOM killer terminated the build process",
    "Apt upgrade interrupted mid-way",
    "Docker daemon failed to start after a VM reboot",
    "Stale PID file prevented service startup",
    "NTP client desynchronized",
    "Inode table overflow occurred",
    "AppArmor profile blocked container networking",
    "Rogue .env file overwrote production config",
    "Swap partition filled up during compilation",
    "Filesystem snapshot rollback reverted recent changes",
]

# Lab-specific context overrides based on GitHub repo analysis
LAB_SPECIFIC_CAUSES = {
    2: [
        "VM deployment pipeline failed during the remote Linux setup",
        "Docker compose on the remote VM refused to start after a reboot",
        "SSH key authentication broke after the VM network reconfiguration",
    ],
    3: [
        "FastAPI migration script corrupted the database schema",
        "Pytest fixtures left dangling database connections",
        "SQLAlchemy session pool exhausted during load testing",
    ],
    4: [
        "Front-end build pipeline failed after the AI agent dependency update",
        "Jest test suite crashed during the front-end integration phase",
        "Agent response parsing failed after the API contract changed",
    ],
    5: [
        "ETL pipeline job failed while syncing the analytics database",
        "Data transformation script hit a type error on the production dataset",
        "Analytics dashboard backend timed out during the aggregation query",
    ],
    6: [
        "Agent tool-calling loop entered an infinite recursion",
        "LLM context window overflowed during the multi-step reasoning task",
        "Agent intent routing failed after the function schema changed",
    ],
    7: [
        "Telegram bot webhook certificate expired on the university VM",
        "Telegram polling loop was blocked by the VM's network restrictions",
        "Bot handler threw an unhandled exception during message processing",
    ],
    8: [
        "Agent interface failed to parse the tool output from the external API",
        "Multi-agent orchestration entered a deadlock state",
        "Agent memory buffer exceeded during the complex workflow execution",
    ],
    9: [
        "Advanced agent workflow failed during the multi-step task orchestration",
        "Agent evaluation pipeline produced inconsistent benchmark results",
        "LangChain agent state machine entered an invalid transition during demo",
    ],
}

CONTEXTS = [
    "On the university VM",
    "During the lab submission process",
    "While building the project Docker container",
    "When uploading to Moodle",
    "During the final push before the Thursday 23:59 deadline",
    "Inside the lab's Docker container environment",
    "While running the CI/CD pipeline on the VM",
    "During the Moodle assignment upload",
    "While testing on the development server",
    "When pulling dependencies during the build",
]

SYMPTOMS = [
    "Causing DNS resolution to fail for the Moodle upload endpoint",
    "Resulting in a 'Connection refused' error on port 8000",
    "Which triggered a 'Permission denied' error on /var/lib/docker",
    "Causing the build to timeout after 30 minutes",
    "Resulting in a 'No space left on device' error",
    "Which caused a segmentation fault during compilation",
    "Resulting in a '502 Bad Gateway' from the reverse proxy",
    "Causing all container health checks to fail",
    "Which made the database connection pool exhaust all available connections",
    "Resulting in a 'Killed' message from the OOM killer",
]

RECOVERY_ATTEMPTS = [
    "Attempted `docker system prune --all` but the operation itself timed out.",
    "Tried restarting the service with `systemctl restart`, but it entered a crash loop.",
    "Ran `fsck` on the volume but found corrupted inodes.",
    "Attempted to roll back to the previous kernel but the GRUB entry was missing.",
    "Tried increasing the disk quota but the VM admin panel was unavailable.",
    "Ran `docker-compose down && docker-compose up -d` but the network bridge was orphaned.",
    "Attempted to clear the cache manually but the tmpfs mount was read-only.",
    "Tried SSH-ing into the container but the network namespace was detached.",
    "Ran `journalctl -xe` for diagnostics but the log partition was also full.",
    "Attempted a hotfix restart but the systemd socket activation failed.",
]

COURSE_SPECIFIC = [
    "This occurred during Lab {lab} submission for the SET course.",
    "The issue prevented on-time submission for Lab {lab} of the SET course.",
    "This directly impacted the Lab {lab} deliverable for the Thursday deadline.",
    "Lab {lab} could not be submitted before 23:59 due to this issue.",
    "The Telegram notification bot on the VM also failed to send a status update due to the network block.",
    "The university VM's Telegram block prevented automated status alerts during troubleshooting.",
]

COURSE_SPECIFIC_GENERAL = [
    "This occurred during the SET course lab submission.",
    "The issue prevented on-time submission for the Thursday deadline.",
    "The university VM's Telegram block prevented automated status alerts during troubleshooting.",
]


def _get_lab_specific_cause(lab_number: int | None) -> str | None:
    """Get a cause specific to the lab based on GitHub repo analysis."""
    if not lab_number:
        return None

    # First check if we have hardcoded lab-specific causes
    if lab_number in LAB_SPECIFIC_CAUSES:
        return random.choice(LAB_SPECIFIC_CAUSES[lab_number])

    # Otherwise, try to get context from GitHub
    lab_context = get_lab_context(lab_number)
    techs = lab_context.get("technologies", [])

    tech_causes = {
        "telegram": "Telegram bot webhook failed to initialize on the university VM",
        "agent": "Agent tool-calling strategy failed during the task execution",
        "data_pipeline": "ETL pipeline job failed while processing the dataset",
        "rest": "REST API endpoint threw an error during the final integration test",
        "docker": "Docker container refused to start on the university VM",
        "database": "Database migration script failed during the schema update",
        "testing": "Test suite failed during the CI pipeline validation",
    }

    for tech in techs:
        if tech in tech_causes:
            return tech_causes[tech]

    return None


def generate_excuse(lab_number: int | None = None) -> str:
    """Generate a random technical excuse by combining template components."""
    # Try to get a lab-specific cause first
    lab_cause = _get_lab_specific_cause(lab_number)
    cause = lab_cause if lab_cause else random.choice(CAUSES)

    context = random.choice(CONTEXTS)
    symptom = random.choice(SYMPTOMS)
    recovery = random.choice(RECOVERY_ATTEMPTS)

    # Build the core excuse
    excuse = f"{cause} {context}, {symptom}. {recovery}"

    # Add course-specific detail with lab number if provided
    if lab_number:
        course_detail = random.choice(COURSE_SPECIFIC).format(lab=lab_number)
    else:
        course_detail = random.choice(COURSE_SPECIFIC_GENERAL)

    excuse += f" {course_detail}"

    return excuse
