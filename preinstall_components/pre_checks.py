import os
import tempfile
import subprocess
from utilities.util_windows_check import check_windows_11_home_or_pro
from utilities.util_error_popup import show_error_popup
from utilities.util_logger import logger
from pathlib import Path
import datetime


def _check_temp_writable() -> bool:
    temp_root = os.environ.get("TEMP", tempfile.gettempdir())
    talon_dir = os.path.join(temp_root, "talon")
    try:
        os.makedirs(talon_dir, exist_ok=True)
        test_path = os.path.join(talon_dir, "_write_test")
        with open(test_path, "w") as f:
            f.write("test")
        os.remove(test_path)
        return True
    except Exception as e:
        logger.error(f"Temp dir check failed: {e}")
        show_error_popup(
            f"Talon could not write files to {talon_dir}.\n"
            "Please free up disk space or check permissions.",
            allow_continue=True,
        )
        return False



def _run_test_script(script_path: str) -> bool:
    try:
        result = subprocess.run(
            [
                "powershell.exe",
                "-NoProfile",
                "-ExecutionPolicy",
                "Bypass",
                "-File",
                script_path,
            ],
            capture_output=True,
            text=True,
            timeout=30,
            creationflags=(
                subprocess.CREATE_NO_WINDOW
                if hasattr(subprocess, "CREATE_NO_WINDOW")
                else 0
            ),
        )
        output = result.stdout.strip()
        logger.debug(f"Test script output: {output}")
        if result.returncode == 0 and "Hello, World!" in output:
            return True
    except Exception as e:
        logger.error(f"Running test PowerShell script failed: {e}")
    show_error_popup(
        "Failed to run test PowerShell script. Powershell may be disabled.",
        allow_continue=True,
    )
    return False

def _check_user(max_days):
    try:
        profile_path = Path.home()
        creation_time = datetime.datetime.fromtimestamp(profile_path.stat().st_birthtime)
        days_since_creation = (datetime.datetime.now() - creation_time).days
        return days_since_creation <= max_days
    except Exception:
        return False

def _check_boot_count(max_boots):
    try:
        cmd = "(Get-WinEvent -FilterHashtable @{LogName='System'; ID=6005} | Measure-Object).Count"
        count = int(subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd]))
        return count <= max_boots
    except Exception:
        return False

def _check_updates(max_updates):
    try:
        cmd = '(New-Object -ComObject "Microsoft.Update.Session").CreateUpdateSearcher().Search("IsInstalled=1").Updates.Count'
        count = int(subprocess.check_output(["powershell", "-NoProfile", "-Command", cmd]))
        return count <= max_updates
    except Exception:
        return False

def check_system(max_days_since_user_creation=7, max_boots=5, max_updates=5):
    if not all([
        _check_user(max_days_since_user_creation),
        _check_boot_count(max_boots),
        _check_updates(max_updates)
    ]):
        logger.warning("Used windows installation detected!")
        show_error_popup("Warning!\nThis device does not appear to have a fresh installation of Windows.\n" \
        "Running Talon on a used system can lead to data loss.\nWe are not able to provide assistance if anything goes wrong beyond this point.", allow_continue=True)


def main() -> None:
    check_windows_11_home_or_pro()
    _check_temp_writable()
    logger.info("Checking windows installation...")
    check_system()



if __name__ == "__main__":
    main()
