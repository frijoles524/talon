import os
import tempfile
import urllib.request
import urllib.error
import subprocess
from utilities.util_defender_check import ensure_defender_disabled
from utilities.util_windows_check import check_windows_11_home_or_pro
from utilities.util_download_handler import download_file
from utilities.util_error_popup import show_error_popup
from utilities.util_logger import logger
from utilities.util_ssl import create_ssl_context
from datetime import datetime, timezone, timedelta
import winreg



TEST_SCRIPT_URL = "https://code.ravendevteam.org/talon/dry_run_test.ps1"



def _check_domain_reachable(url: str) -> bool:
    ctx = create_ssl_context()
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10, context=ctx):
            return True
    except Exception as e:
        logger.error(f"Connectivity check failed for {url}: {e}")
        show_error_popup(
            "Talon could not reach code.ravendevteam.org.\n"
            "Please check your internet connection or contact your ISP.",
            allow_continue=True,
        )
        return False



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



def _download_and_run_test_script() -> bool:
    if not download_file(TEST_SCRIPT_URL, dest_name="dry_run_test.ps1"):
        return False
    temp_root = os.environ.get("TEMP", tempfile.gettempdir())
    script_path = os.path.join(temp_root, "talon", "dry_run_test.ps1")
    return _run_test_script(script_path)


def ensure_fresh_install() -> bool:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                         r"SOFTWARE\Microsoft\Windows NT\CurrentVersion")
        install_date_seconds, _ = winreg.QueryValueEx(key, "InstallDate")
        install_date = datetime.fromtimestamp(install_date_seconds, timezone.utc)
        now = datetime.now(timezone.utc)
        delta = now - install_date
        return delta < timedelta(days=1)


def main() -> None:
    ensure_defender_disabled()
    check_windows_11_home_or_pro()
    _check_domain_reachable("https://code.ravendevteam.org")
    _check_temp_writable()
    _download_and_run_test_script()

if __name__ == "__main__":
    main()
    
