import os
import sys
import json
import tempfile
import subprocess
from utilities.util_logger import logger
from utilities.util_error_popup import show_error_popup
from utilities.util_powershell_handler import run_powershell_command



def load_choice() -> str:
	temp_dir = os.environ.get('TEMP', tempfile.gettempdir())
	choice_file = os.path.join(temp_dir, 'talon', 'browser_choice.json')
	if not os.path.exists(choice_file):
		raise FileNotFoundError(f"Browser choice file not found: {choice_file}")
	with open(choice_file, 'r') as f:
		data = json.load(f)
	browser = data.get('browser')
	if not browser:
		raise ValueError(f"No 'browser' key in {choice_file}")
	return browser



def ensure_chocolatey():
	try:
		subprocess.run(
			["choco", "-v"],
			check=True,
			stdout=subprocess.DEVNULL,
			stderr=subprocess.DEVNULL
		)
		logger.info("Chocolatey already installed.")
	except (subprocess.CalledProcessError, FileNotFoundError):
		logger.info("Chocolatey not found. Installing now...")
		install_cmd = (
			"Set-ExecutionPolicy Bypass -Scope Process -Force; "
			"[System.Net.ServicePointManager]::SecurityProtocol = "
			"[System.Net.ServicePointManager]::SecurityProtocol -bor 3072; "
			"iex ((New-Object System.Net.WebClient).DownloadString("
			"'https://community.chocolatey.org/install.ps1'))"
		)
		logger.info(f"Running install command: {install_cmd}")
		try:
			run_powershell_command(install_cmd)
			logger.info("Chocolatey install script executed.")
			choco_exe = _get_choco_exe()
			subprocess.run(
				[choco_exe, "-v"],
				check=True,
				stdout=subprocess.DEVNULL,
				stderr=subprocess.DEVNULL
			)
			logger.info("Chocolatey installed and verified.")
		except Exception as e:
			logger.error(f"Failed to install or verify Chocolatey: {e}")
			show_error_popup(
				f"Failed to install or verify Chocolatey:\n{e}",
				allow_continue=False
			)
			sys.exit(1)



def _get_choco_exe() -> str:
	env_path = os.environ.get("ChocolateyInstall")
	if env_path:
		choco = os.path.join(env_path, "bin", "choco.exe")
		if os.path.exists(choco):
			return choco
	default_path = os.path.join(
		os.environ.get("ProgramData", r"C:\\ProgramData"),
		"chocolatey",
		"bin",
		"choco.exe",
	)
	return default_path if os.path.exists(default_path) else "choco"



def _install_choco_package(pkg_id: str, display_name: str):
	choco_exe = _get_choco_exe()
	logger.info(f"Installing via Chocolatey: {display_name} ({pkg_id})")
	try:
		result = subprocess.run(
			[choco_exe, "install", pkg_id, "-y"],
			check=False
		)
		if result.returncode in (0, 3010):
			if result.returncode == 3010:
				logger.info(f"Successfully installed {display_name}, reboot required.")
			else:
				logger.info(f"Successfully installed {display_name}.")
			return
		logger.error(f"Chocolatey exited with code {result.returncode} for {pkg_id}")
		show_error_popup(
			"A problem occurred with Chocolatey during installation. "
			f"'{display_name}' could not be installed successfully.\n"
			f"Chocolatey exit code: {result.returncode}",
			allow_continue=True
		)
	except Exception as e:
		logger.error(f"Unexpected error installing {pkg_id}: {e}")
		show_error_popup(
			"A problem occurred with Chocolatey during installation. "
			f"'{display_name}' could not be installed successfully.\n"
			f"Error: {e}",
			allow_continue=True
		)



def install_vcredist():
	# Some people may say see this and say "why is a DEBLOATER installing BLOAT!?"
	# This step is necessary to install dependencies that a very, very large amount of
	# modern programs rely on. For example, Waterfox. These dependencies cannot reasonably
	# be considered "bloat" as bloat is unnecessary, while these dependencies, a very large
	# amount of the time, are necessary.
	_install_choco_package("vcredist140", "Microsoft Visual C++ 2015–2022 Redistributable")



def install_browser(pkg_id: str):
	_install_choco_package(pkg_id, f"browser '{pkg_id}'")



def main():
	try:
		pkg_id = load_choice()
		logger.info(f"Browser selected: {pkg_id}")
	except Exception as e:
		logger.error(f"Error reading browser choice: {e}")
		show_error_popup(f"Internal error reading browser choice:\n{e}", allow_continue=False)
		sys.exit(1)
	ensure_chocolatey()
	install_vcredist()
	install_browser(pkg_id)



if __name__ == "__main__":
	main()