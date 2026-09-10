"""OTA auto-update support via git."""

import os
import subprocess
import sys

from . import config
from .display_renderer import DisplayRenderer


def check_for_updates(renderer: DisplayRenderer):
    """Fetch from origin and, if behind, pull and restart the process."""
    cwd = str(config.PROJECT_ROOT)
    try:
        subprocess.run(
            ["git", "fetch"],
            check=True,
            cwd=cwd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        result = subprocess.run(
            ["git", "status", "-uno"], capture_output=True, text=True, check=False, cwd=cwd
        )
        if "Your branch is behind" not in result.stdout:
            return

        print("New update detected! Pulling from repository...")
        renderer.display_epileptic_countdown("UPDATING...", hold_time=1.0)
        subprocess.run(["git", "pull", "--rebase", "--autostash"], check=True, cwd=cwd)
        print("Update successful. Restarting script...")
        renderer.clear()
        os.execv(sys.executable, ["python3", *sys.argv])
    except Exception as exc:
        print(f"Auto-update failed: {exc}")