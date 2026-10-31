EyeGuard - User Guide (English)
================================

WHAT IT IS
----------
An eye-protection reminder for Windows. After you log in, it runs silently
in the background with no window and no console - only a small green dot in
the system tray. Using your webcam, it checks locally whether you are looking
at the screen. Once you have been watching continuously for 30 minutes, it
forces a full-screen "Aerial-style" green nature video break and speaks
"Take a break" out loud.

QUICK START
-----------
1. Auto-start is already configured. It will run automatically from your next
   login (or reboot).
2. To start it right now: double-click EyeGuard.pyw in this folder.
3. A green dot appears in the system tray. Right-click it for:
   - Take a break now   : trigger the break screen immediately (for testing)
   - Pause monitoring   : pause / resume the timer
   - Exit EyeGuard      : quit the program completely
4. The break screen plays for 20 seconds, then closes automatically and the
   30-minute timer restarts.

PRIVACY
-------
Webcam frames are processed entirely on this computer. Nothing is uploaded,
recorded or saved.

SETTINGS (config.json - open with Notepad)
------------------------------------------
- interval_min : how long before a break, in minutes (default 30; e.g. 10/20/45/60)
- break_sec    : length of each break, in seconds (default 20)
- use_camera   : set to false to disable the webcam and use pure timing mode
Save the file, then exit and restart EyeGuard for changes to take effect.

NOTES
-----
- If no webcam is available (or it is being used by another app), EyeGuard
  automatically falls back to pure timing mode.
- The break screen is rendered by Chrome (or Edge) in kiosk mode, which covers
  the Windows taskbar. If Chrome/Edge is missing, EyeGuard falls back to voice
  reminders only.
- EyeGuard runs on the Python runtime bundled with WorkBuddy. If WorkBuddy is
  uninstalled later, EyeGuard will stop working - see the uninstall steps below.

UNINSTALL
---------
1. Right-click the tray icon -> Exit EyeGuard
2. Open the Run dialog (Win+R), type: regedit
   Delete this value:  HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
   -> EyeGuard
   (Or in PowerShell:
    Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'EyeGuard')
3. Delete the folder:  C:\Users\Public\EyeGuard

FILES
-----
EyeGuard.pyw                        main program (silent background monitor)
rest.html                           full-screen break page (video + voice)
rest-aerial.mp4 / rest-plant.mp4    break-screen nature videos (Aerial style)
rest-bg.png                         fallback background image
haarcascade_frontalface_default.xml face-detection model
config.json                         settings
eyeguard.log                        runtime log (created automatically)
