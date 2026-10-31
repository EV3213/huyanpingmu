EyeGuard - User Guide
================================

【WHAT IT IS】
An eye-protection reminder program: it runs silently in the background after boot (no window, no interface), uses the webcam to detect locally whether you are looking at the screen, and once you have been watching for 30 minutes it forces a full-screen "Aerial-style" green nature video break screen and speaks "Take a break" out loud.

【HOW TO USE】
1. Auto-start at boot is already configured; it takes effect from the next boot.
2. To try it right away: double-click EyeGuard.pyw to launch it.
3. After launch, a green dot icon appears in the system tray at the bottom right:
   - Take a break now: enter the break screen immediately (for testing)
   - Pause monitoring: pause / resume the timer
   - Exit EyeGuard: quit completely
4. The break screen plays full-screen for 20 seconds; when the countdown ends it closes automatically and the timer restarts.
5. Webcam video is processed only on this machine - no network, no saving, no uploading.

【SETTINGS】(open config.json with Notepad to edit)
- interval_min: how long before a break (default 30 minutes; can be set to 10/20/45/60)
- break_sec: length of a break in seconds (default 20)
- use_camera: set to false to turn off the webcam and switch to pure timing mode
Save after editing, then exit and restart the program for changes to take effect.

【NOTES】
- If the break screen is covered by another window the first time it appears, that is normal (always-on-top takes effect automatically).
- If the webcam is occupied or not connected, it automatically falls back to "pure timing mode".
- This program depends on the Python runtime bundled with WorkBuddy; if uninstalling WorkBuddy later makes it stop working, just delete this folder and the startup entry in the registry.

【HOW TO UNINSTALL】
1. Right-click the tray icon -> Exit EyeGuard
2. Delete the autostart entry: open Registry Editor (Win+R, type regedit) and delete the value "EyeGuard" under HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run
3. Delete the whole folder C:\Users\Public\EyeGuard
