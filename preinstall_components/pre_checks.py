import os
import tempfile
import subprocess
from utilities.util_windows_check import check_windows_11_home_or_pro
from utilities.util_error_popup import show_error_popup
from utilities.util_logger import logger
import datetime
import win32evtlog
import win32com.client



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

def _check_user(max_days_since_creation=7):
    profile_path = rf"C:\Users\{os.getlogin()}"
    if not profile_path:
        return False
    try:
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(profile_path))
        days_since_creation = (datetime.datetime.now() - creation_time).days
        return days_since_creation <= max_days_since_creation
    except Exception:
        return False

def _check_boot_count(max_boots=5):
    try:
        server = 'localhost'
        source = 'System'
        handle = win32evtlog.OpenEventLog(server, source)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        boot_events_count = 0
        while True:
            events = win32evtlog.ReadEventLog(handle, flags, 0)
            if not events:
                break
            for e in events:
                if e.SourceName == 'Microsoft-Windows-Kernel-Boot':
                    boot_events_count += 1
        return boot_events_count <= max_boots
    except Exception:
        return False

def _check_updates(max_updates=5):
    try:
        session = win32com.client.Dispatch("Microsoft.Update.Session")
        searcher = session.CreateUpdateSearcher()
        search_result = searcher.Search("IsInstalled=1")
        updates_count = search_result.Updates.Count
        return updates_count <= max_updates
    except Exception as e:
        print("Error:", e)
        return False

def check_system(max_days_since_user_creation=7, max_boots=5, max_updates=5):
    checks = [
        _check_user(max_days_since_user_creation),
        _check_boot_count(max_boots),
        _check_updates(max_updates)
    ]
    return all(checks)

def main() -> None:
    check_windows_11_home_or_pro()
    _check_temp_writable()
    logger.info("Checking windows installation...")
    if not check_system():
        logger.warning("Used windows installation detected!")
        show_error_popup("Warning!\nThis device does not appear to have a fresh installation of Windows.\nRunning Talon on a used system can lead to data loss.\nWe are not able to provide assistance if anything goes wrong beyond this point.", allow_continue=True)



if __name__ == "__main__":
    main()
