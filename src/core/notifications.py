"""
Desktop notifications management module for the browserAPI project.
Sends native balloon/toast notifications on Linux (notify-send) and Windows (PowerShell balloon tip).
"""

import subprocess
import sys

def send_desktop_notification(title: str, message: str) -> None:
    """
    Sends a native desktop notification on Linux and Windows.
    Uses no external python dependencies to ensure portable execution.
    """
    try:
        if sys.platform.startswith("linux"):
            # Trigger standard Linux notify-send
            subprocess.run(["notify-send", title, message], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif sys.platform == "win32":
            # Trigger Windows Forms BalloonTip via PowerShell
            ps_script = f"""
            [void] [System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
            $notification = New-Object System.Windows.Forms.NotifyIcon
            $notification.Icon = [System.Drawing.SystemIcons]::Warning
            $notification.BalloonTipIcon = 'Warning'
            $notification.BalloonTipTitle = '{title}'
            $notification.BalloonTipText = '{message}'
            $notification.Visible = $True
            $notification.ShowBalloonTip(5000)
            """
            subprocess.run(["powershell", "-Command", ps_script], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f" [-] Failed to send desktop notification: {e}")
