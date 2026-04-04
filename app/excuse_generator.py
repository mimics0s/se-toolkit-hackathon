"""Excuse generation logic using template-based randomization."""

import random

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

# Fallback course-specific templates without lab number
COURSE_SPECIFIC_GENERAL = [
    "This occurred during the SET course lab submission.",
    "The issue prevented on-time submission for the Thursday deadline.",
    "The university VM's Telegram block prevented automated status alerts during troubleshooting.",
]


def generate_excuse(lab_number: int | None = None) -> str:
    """Generate a random technical excuse by combining template components."""
    cause = random.choice(CAUSES).capitalize()
    context = random.choice(CONTEXTS).capitalize()
    symptom = random.choice(SYMPTOMS).capitalize()
    recovery = random.choice(RECOVERY_ATTEMPTS).capitalize()

    # Build the core excuse
    excuse = f"{cause} {context}, {symptom}. {recovery}"

    # Add course-specific detail with lab number if provided
    if lab_number:
        course_detail = random.choice(COURSE_SPECIFIC).format(lab=lab_number)
    else:
        course_detail = random.choice(COURSE_SPECIFIC_GENERAL)

    excuse += f" {course_detail}"

    return excuse
