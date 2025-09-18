import os
import sys
import re
from utilities.util_logger import logger
from utilities.util_powershell_handler import run_powershell_command
from utilities.util_error_popup import show_error_popup



def main():
<<<<<<< HEAD
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
	logger.info("Executing patched ChrisTitusTech WinUtil via bundled script")
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
	logger.info("Executing Raphi Win11Debloat via bundled script")
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
=======
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
    
    winutil_dir = os.environ.get('TEMP', '/tmp')
    winutil_path = os.path.join(winutil_dir, 'talon', 'winutil.ps1')
    if not os.path.exists(winutil_path):
        logger.error(f"WinUtil script not found: {winutil_path}")
        try:
            show_error_popup(
                f"WinUtil script not found:\n{winutil_path}",
                allow_continue=False,
            )
        except Exception:
            pass
        sys.exit(1)
    
    # Patch the script with regex
    logger.info("Patching ChrisTitusTech WinUtil script to remove Invoke-WPFFeatureInstall pop-up")
    try:
        with open(winutil_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        # Remove the feature install block and following wait loop
        feature_regex = r'(?ms)^\s*Write-Host "Installing features\.\.\."\s*.*?Write-Host "Done\."'
        replacement = 'Write-Host "Features installation skipped"\n'
        patched_script = re.sub(feature_regex, replacement, script_content)
        with open(winutil_path, 'w', encoding='utf-8') as f:
            f.write(patched_script)
        logger.info("Patched winutil.ps1 to disable Invoke-WPFFeatureInstall.")
    except Exception as e:
        logger.error(f"Failed to patch ChrisTitusTech WinUtil: {e}")
        try:
            show_error_popup(
                f"Failed to patch ChrisTitusTech WinUtil: {e}",
                allow_continue=False,
            )
        except Exception:
            pass
        sys.exit(1)
    # Execute the patched script
    cmd1 = f"& '{winutil_path}' -Config '{config_path}' -Run -NoUI"
    logger.info("Executing patched ChrisTitusTech WinUtil via local script")
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
    args2 = [
        '-Silent',
        '-RemoveApps',
        '-RemoveGamingApps',
        '-DisableTelemetry',
        '-DisableBing',
        '-DisableSuggestions',
        '-DisableLockscreenTips',
        '-DisableSettings365Ads',
        '-RevertContextMenu',
        '-TaskbarAlignLeft',
        '-HideSearchTb',
        '-DisableWidgets',
        '-DisableCopilot',
        '-DisableNotepadAI',
        '-DisablePaintAI',
        '-ClearStartAllUsers',
        '-DisableDVR',
        '-DisableStartRecommended',
        '-ExplorerToThisPC',
        '-DisableMouseAcceleration',
    ]
    flags = ' '.join(args2)
    cmd2 = f"& ([scriptblock]::Create((irm \"https://debloat.raphi.re/\"))) {flags}"
    logger.info("Executing Raphi Win11Debloat via remote command")
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
>>>>>>> 8a21af6179264311b3f619071c059cde1e5c8f15



if __name__ == "__main__":
	main()
