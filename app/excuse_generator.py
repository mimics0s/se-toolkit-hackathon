"""Excuse generation logic using template-based randomization."""

import random

# Template components for generating realistic technical excuses
CAUSES = [
    "Docker build cache became corrupted",
    "systemd-resolved service entered a restart loop",
    "disk quota was exceeded",
    "the Ubuntu 24.04 kernel update broke the network driver",
    "a misconfigured cron job triggered an unexpected cleanup",
    "the OOM killer terminated the build process",
    "an apt upgrade interrupted mid-way",
    "the Docker daemon failed to start after a VM reboot",
    "a stale PID file prevented service startup",
    "the NTP client desynchronized",
    "an inode table overflow occurred",
    "the AppArmor profile blocked container networking",
    "a rogue .env file overwrote production config",
    "the swap partition filled up during compilation",
    "a filesystem snapshot rollback reverted recent changes",
]

CONTEXTS = [
    "on the university VM",
    "during the lab submission process",
    "while building the project Docker container",
    "when uploading to Moodle",
    "during the final push before the Thursday 23:59 deadline",
    "inside the lab's Docker container environment",
    "while running the CI/CD pipeline on the VM",
    "during the Moodle assignment upload",
    "while testing on the development server",
    "when pulling dependencies during the build",
]

SYMPTOMS = [
    "causing DNS resolution to fail for the Moodle upload endpoint",
    "resulting in a 'Connection refused' error on port 8000",
    "which triggered a 'Permission denied' error on /var/lib/docker",
    "causing the build to timeout after 30 minutes",
    "resulting in a 'No space left on device' error",
    "which caused a segmentation fault during compilation",
    "resulting in a '502 Bad Gateway' from the reverse proxy",
    "causing all container health checks to fail",
    "which made the database connection pool exhaust all available connections",
    "resulting in a 'Killed' message from the OOM killer",
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


def generate_excuse(lab_number: int | None = None) -> str:
    """Generate a random technical excuse by combining template components."""
    cause = random.choice(CAUSES)
    context = random.choice(CONTEXTS)
    symptom = random.choice(SYMPTOMS)
    recovery = random.choice(RECOVERY_ATTEMPTS)

    # Build the core excuse
    excuse = f"{cause} {context}, {symptom}. {recovery}"

    # Add course-specific detail with lab number if provided
    if lab_number:
        course_detail = random.choice(COURSE_SPECIFIC).format(lab=lab_number)
    else:
        # Use templates that don't require lab number
        course_detail = random.choice([
            "This occurred during the SET course lab submission.",
            "The issue prevented on-time submission for the Thursday deadline.",
            "The university VM's Telegram block prevented automated status alerts during troubleshooting.",
        ])

    excuse += f" {course_detail}"

    return excuse
