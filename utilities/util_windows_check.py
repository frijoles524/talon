import os
import sys
import win32com.client
import winreg
import datetime
import win32evtlog
from utilities.util_logger import logger
from utilities.util_error_popup import show_error_popup



def _read_registry_value(name: str) -> str:
    key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
    access = winreg.KEY_READ
    if hasattr(winreg, "KEY_WOW64_64KEY"):
        access |= winreg.KEY_WOW64_64KEY
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, access) as key:
            val, _ = winreg.QueryValueEx(key, name)
        return str(val)
    except Exception as e:
        logger.exception(f"Unable to read registry value {name}: {e}")
        raise



def check_windows_11_home_or_pro() -> str:
    if sys.platform != "win32":
        show_error_popup(
            "Unsupported OS detected.\n"
            "This tool requires Windows 11 Home or Professional.",
            allow_continue=False
        )
    try:
        product_name = _read_registry_value("ProductName")
        build_str    = _read_registry_value("CurrentBuildNumber")
        build_num    = int(build_str)
    except Exception:
        show_error_popup(
            "Failed to determine Windows version.\n"
            "This tool requires Windows 11 Home or Professional.",
            allow_continue=False
        )
    is_win11 = (
        product_name.startswith("Windows 11")
        or (product_name.startswith("Windows 10") and build_num >= 22000)
    )
    if not is_win11:
        show_error_popup(
            f"Incompatible Windows version detected:\n"
            f"  {product_name} (build {build_num})\n"
            "This tool requires Windows 11 Home or Professional.",
            allow_continue=False
        )
    if "Home" in product_name:
        edition = "Home"
    elif "Professional" in product_name or "Pro" in product_name or "Enterprise" in product_name:
        edition = "Professional"
    else:
        show_error_popup(
            f"Unsupported Windows 11 edition detected:\n"
            f"  {product_name}\n"
            "Only Home or Professional editions are supported.",
            allow_continue=False
        )
    logger.info(f"Detected OS: {product_name} (build {build_num}); edition: {edition}")
    return edition

def get_user():
    return rf"C:\Users\{os.getlogin()}"

def check_user(max_days_since_creation=7):
    profile_path = get_user()
    if not profile_path:
        return False
    try:
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(profile_path))
        days_since_creation = (datetime.datetime.now() - creation_time).days
        return days_since_creation <= max_days_since_creation
    except Exception:
        return False

def check_boot_count(max_boots=5):
    try:
        server = 'localhost'
        logtype = 'System'
        handle = win32evtlog.OpenEventLog(server, logtype)
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

def check_updates(max_updates=5):
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
        check_user(max_days_since_user_creation),
        check_boot_count(max_boots),
        check_updates(max_updates)
    ]
    return all(checks)


if __name__ == "__main__":
    ed = check_windows_11_home_or_pro()
    print(f"Windows 11 {ed} detected. Continuing…")