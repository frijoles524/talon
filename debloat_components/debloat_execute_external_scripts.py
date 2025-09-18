import os
import sys
import re
from utilities.util_logger import logger
from utilities.util_powershell_handler import run_powershell_command
from utilities.util_error_popup import show_error_popup



def main():
	if getattr(sys, 'frozen', False):
		base_path = os.path.dirname(sys.executable)
	else:
		components_dir = os.path.dirname(os.path.abspath(__file__))
		base_path = os.path.dirname(components_dir)
	config_path = os.path.join(base_path, 'configs', 'default.json')
	if not os.path.exists(config_path):
		logger.error(f"WinUtil config not found: {config_path}")
		try:
			show_error_popup(
				f"WinUtil config not found:\n{config_path}",
				allow_continue=False,
			)
		except Exception:
			pass
		sys.exit(1)
	logger.info(f"Using WinUtil config: {config_path}")
	winutil_path = os.path.join(base_path, 'external_scripts', 'winutil.ps1')
	if not os.path.exists(winutil_path):
		logger.error(f"Bundled WinUtil script not found: {winutil_path}")
		try:
			show_error_popup(
				f"Bundled WinUtil script not found:\n{winutil_path}",
				allow_continue=False
			)
		except Exception:
			pass
		sys.exit(1)
	cmd1 = f"& '{winutil_path}' -Config '{config_path}' -Run -NoUI"
	logger.info("Executing ChrisTitusTech WinUtil")
	try:
		run_powershell_command(
			cmd1,
			monitor_output=True,
			termination_str='Tweaks are Finished',
		)
		logger.info("Successfully executed ChrisTitusTech WinUtil")
	except Exception as e:
		logger.error(f"Failed to execute ChrisTitusTech WinUtil: {e}")
		try:
			show_error_popup(
				f"Failed to execute ChrisTitusTech WinUtil:\n{e}",
				allow_continue=False,
			)
		except Exception:
			pass
		sys.exit(1)
	win11debloat_path = os.path.join(base_path, 'external_scripts', 'win11debloat.ps1')
	if not os.path.exists(win11debloat_path):
		logger.error(f"Bundled Win11Debloat script not found: {win11debloat_path}")
		try:
			show_error_popup(
				f"Bundled Win11Debloat script not found:\n{win11debloat_path}",
				allow_continue=False
			)
		except Exception:
			pass
		sys.exit(1)
	args2 = [
		'-Silent',
		'-RemoveApps',
		'-RemoveGamingApps',
		'-DisableTelemetry',
		'-DisableBing',
		'-DisableSuggestions',
		'-DisableLockscreenTips',
		'-RevertContextMenu',
		'-TaskbarAlignLeft',
		'-HideSearchTb',
		'-DisableWidgets',
		'-DisableCopilot',
		'-ClearStartAllUsers',
		'-DisableDVR',
		'-DisableStartRecommended',
		'-ExplorerToThisPC',
		'-DisableMouseAcceleration',
		'-DisableDesktopSpotlight',
		'-DisableSettings365Ads',
		'-DisableSettingsHome',
		'-DisablePaintAI',
		'-DisableNotepadAI',
		'-DisableStickyKeys',
	]
	flags = ' '.join(args2)
	cmd2 = f"& '{win11debloat_path}' {flags}"
	logger.info("Executing Raphi Win11Debloat")
	try:
		run_powershell_command(cmd2)
		logger.info("Successfully executed Raphi Win11Debloat")
	except Exception as e:
		logger.error(f"Failed to execute Raphi Win11Debloat: {e}")
		try:
			show_error_popup(
				f"Failed to execute Raphi Win11Debloat:\n{e}",
				allow_continue=False
			)
		except Exception:
			pass
		sys.exit(1)

	logger.info("All external debloat scripts executed successfully.")



if __name__ == "__main__":
	main()
