import datetime
import subprocess
import os

import hues

import settings


def write_powershell_script(script_content):
    """Writes a PowerShell script to a file."""
    script_file = settings.script_file
    with open(script_file, "w") as f:
        f.write(script_content)


def run_powershell_script():
    """Runs a PowerShell script."""
    path_to_script = r"C:\Users\zxceb\PycharmProjects\UchebPrac\reload_logs.ps1"
    subprocess.run(["powershell.exe", "-Command", f"{path_to_script}"])


def main():
    script_path = settings.script_path
    task_name = settings.task_name

    powershell_script = f'''
    $scriptPath = "{script_path}"
    $taskName = "{task_name}"
    $action = New-ScheduledTaskAction -Execute "python.exe" -Argument $scriptPath
    $trigger = New-ScheduledTaskTrigger -Daily -At "00:00"
    $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Settings $settings
    '''

    write_powershell_script(powershell_script)
    hues.info(f"Schedule added Daily At ""00:00"" min started")

