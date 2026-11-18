"""Desktop notification engine and systemd user timer integration.

Strictly NO emojis. Clean ASCII symbols.
"""

import os
import shutil
import subprocess
import random
from pathlib import Path
from typing import Optional, Tuple, Dict, Any, List
from datetime import datetime

from .database import Database
from .models import AntiProcrastinationTask
from .burns_methods import BURNS_METHODS
from .cbt_data import COGNITIVE_DISTORTIONS


def send_notification(title: str, message: str, urgency: str = "normal") -> bool:
    """Send desktop notification via notify-send. Returns True if successful."""
    notify_bin = shutil.which("notify-send")
    if not notify_bin:
        return False

    cmd = [
        notify_bin,
        "-a", "Leahe CBT",
        "-u", urgency,
        title,
        message,
    ]

    try:
        res = subprocess.run(cmd, capture_output=True, timeout=5)
        return res.returncode == 0
    except Exception:
        return False


def get_smart_reminder_content(db: Database) -> Tuple[str, str]:
    """Generate intelligent CBT practice reminder based on pending activities and user state."""
    # 1. Check for pending behavioral experiments (Fear testing)
    pending_exps = db.list_experiments(status="pending")
    if pending_exps:
        exp = pending_exps[0]
        title = "Leahe: Behavioral Experiment Check"
        msg = (
            f"Fear test pending: \"{exp.title}\". "
            f"Feared outcome: \"{exp.fear_prediction}\". Did you test it? Run 'leahy experiment complete {exp.id}' to record what happened!"
        )
        return title, msg

    # 2. Check for pending pleasure-prediction activities
    pending_tasks = db.list_tasks(status="pending")
    if pending_tasks:
        task = pending_tasks[0]
        title = "Leahe: Pleasure Prediction Check"
        msg = (
            f"Pending activity: \"{task.task_name}\" (Predicted pleasure: {task.predicted_pleasure}%). "
            f"Did you complete it? Run 'leahy complete {task.id}' to record actual pleasure!"
        )
        return title, msg

    # 3. Check for pending behavioral action steps (Follow-up)
    pending_actions = db.list_actions(is_done=False)
    if pending_actions:
        action = pending_actions[0]
        title = "Leahe: Action Commitment Follow-up"
        msg = (
            f"Action step follow-up: \"{action.action_text}\". "
            f"Did you take this step? Run 'leahy actions --done {action.id}' when completed!"
        )
        return title, msg

    # 4. Check recent entries
    recent = db.list_entries(limit=1)
    if not recent:
        title = "Leahe: Daily CBT Practice"
        msg = "Ready for your first check-in? Run 'leahy check' or 'leahy note' to log your mood."
        return title, msg

    last_entry = recent[0]
    time_diff = datetime.now() - last_entry.parsed_datetime
    if time_diff.total_seconds() > 14 * 3600:
        title = "Leahe: Mindful Check-in"
        msg = "Take 30 seconds to rate your mood and energy. Run 'leahy check' or 'leahy note'."
        return title, msg

    # 3. Rotate a Burns cognitive restructuring tip or distortion antidote
    tips = [
        (
            "Pleasure Predicting Lab",
            "Fearing a difficult task? Run 'leahy predict' to test whether reality is better than expectation.",
        ),
        (
            "The Double-Standard Technique",
            "Would you speak to a dear friend as harshly as you speak to yourself right now?",
        ),
        (
            "Cost-Benefit Analysis",
            "What are the emotional advantages vs painful costs of holding onto this standard?",
        ),
        (
            "Thinking in Shades of Grey",
            "Things are rarely 0% or 100%. Where does this reality fall on a 0-100% continuum?",
        ),
        (
            "Rapid 3-Column Thought Buster",
            "Caught in a negative loop? Run 'leahy 3col' to dismantle negative automatic thoughts.",
        ),
    ]
    chosen_title, chosen_msg = random.choice(tips)
    return f"Leahe Tip: {chosen_title}", chosen_msg


def get_systemd_user_dir() -> Path:
    """Return ~/.config/systemd/user directory."""
    return Path.home() / ".config" / "systemd" / "user"


def get_leahy_executable_path() -> str:
    """Find the best executable path for systemd service ExecStart."""
    # Prefer ~/.local/bin/leahy
    user_bin = Path.home() / ".local" / "bin" / "leahy"
    if user_bin.exists():
        return str(user_bin.resolve())

    which_leahy = shutil.which("leahy")
    if which_leahy:
        return which_leahy

    project_root = Path(__file__).resolve().parent.parent.parent
    local_script = project_root / "leahy"
    if local_script.exists():
        return str(local_script.resolve())

    return "leahy"


def generate_service_unit_content(exec_cmd: Optional[str] = None) -> str:
    """Generate systemd service unit string."""
    command = exec_cmd or f"{get_leahy_executable_path()} notify"
    user_path = f"{Path.home() / '.local' / 'bin'}:/usr/local/bin:/usr/bin:/bin"

    return f"""[Unit]
Description=Leahe CBT Practice & Mood Notification Service
After=default.target

[Service]
Type=oneshot
ExecStart={command}
Environment="PATH={user_path}"
"""


def generate_timer_unit_content(schedule: str = "*-*-* 10,14,18,21:00:00") -> str:
    """Generate systemd timer unit string."""
    return f"""[Unit]
Description=Leahe CBT Practice Notification Timer

[Timer]
OnCalendar={schedule}
Persistent=true

[Install]
WantedBy=timers.target
"""


def install_systemd_timer(
    schedule: str = "*-*-* 10,14,18,21:00:00",
    custom_dir: Optional[Path] = None,
    exec_cmd: Optional[str] = None,
) -> Dict[str, Any]:
    """Write systemd service and timer files, and attempt to enable them."""
    user_dir = custom_dir or get_systemd_user_dir()
    user_dir.mkdir(parents=True, exist_ok=True)

    service_file = user_dir / "leahy-reminder.service"
    timer_file = user_dir / "leahy-reminder.timer"

    service_file.write_text(generate_service_unit_content(exec_cmd), encoding="utf-8")
    timer_file.write_text(generate_timer_unit_content(schedule), encoding="utf-8")

    result = {
        "service_path": service_file,
        "timer_path": timer_file,
        "enabled": False,
        "error": None,
    }

    # Attempt to reload and enable via systemctl --user
    try:
        r1 = subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True, text=True, timeout=5)
        if r1.returncode == 0:
            r2 = subprocess.run(["systemctl", "--user", "enable", "--now", "leahy-reminder.timer"], capture_output=True, text=True, timeout=5)
            if r2.returncode == 0:
                result["enabled"] = True
            else:
                result["error"] = r2.stderr.strip()
        else:
            result["error"] = r1.stderr.strip()
    except Exception as ex:
        result["error"] = str(ex)

    return result


def uninstall_systemd_timer(custom_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Stop, disable and remove systemd timer and service units."""
    user_dir = custom_dir or get_systemd_user_dir()
    service_file = user_dir / "leahy-reminder.service"
    timer_file = user_dir / "leahy-reminder.timer"

    try:
        subprocess.run(["systemctl", "--user", "disable", "--now", "leahy-reminder.timer"], capture_output=True, timeout=5)
    except Exception:
        pass

    removed_service = False
    removed_timer = False

    if service_file.exists():
        service_file.unlink()
        removed_service = True

    if timer_file.exists():
        timer_file.unlink()
        removed_timer = True

    try:
        subprocess.run(["systemctl", "--user", "daemon-reload"], capture_output=True, timeout=5)
    except Exception:
        pass

    return {
        "service_removed": removed_service,
        "timer_removed": removed_timer,
    }


def get_systemd_timer_status(custom_dir: Optional[Path] = None) -> Dict[str, Any]:
    """Check whether systemd timer is installed and active."""
    user_dir = custom_dir or get_systemd_user_dir()
    timer_file = user_dir / "leahy-reminder.timer"
    service_file = user_dir / "leahy-reminder.service"

    installed = timer_file.exists() and service_file.exists()
    active = False
    schedule = "N/A"

    if installed:
        try:
            content = timer_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                if line.startswith("OnCalendar="):
                    schedule = line.split("=", 1)[1].strip()
        except Exception:
            pass

        try:
            res = subprocess.run(["systemctl", "--user", "is-active", "leahy-reminder.timer"], capture_output=True, text=True, timeout=3)
            active = (res.returncode == 0 and res.stdout.strip() == "active")
        except Exception:
            pass

    return {
        "installed": installed,
        "active": active,
        "schedule": schedule,
        "service_file": service_file,
        "timer_file": timer_file,
    }
