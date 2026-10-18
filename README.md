<img src="assets/icon.svg" width="64" height="64" alt="">

# Multi Click for Windows

Turn one physical left click into 5, 10, or a custom number of total clicks in other Windows applications.

## Run

1. On **Windows 10 or 11**, install **Python 3.10 or newer** from [python.org](https://www.python.org/downloads/windows/). Keep the installer’s **Tcl/Tk and IDLE** option enabled.
2. Download or copy this project folder to your Windows computer.
3. Double-click **start.bat**.

No pip packages, administrator access, or internet connection are needed to run the app after installing Python. You can also launch it from this folder with `py -3 -m multiclick`.

## Use

- Choose **2×, 5×, 10×, 20×**, or enter a custom multiplier from **2 to 100**.
- Set spacing between extra clicks from **10 to 1000 milliseconds** (default: 40 ms).
- Press **F6** or click **Enable multiplier**. The app starts paused.
- Click in another application. At 5×, your original click is followed by **4 extra clicks** after you release the left mouse button.
- Press **F6** to pause or **F8** to stop and cancel pending clicks. These shortcuts work while another app has focus. Closing Multi Click also stops it.

Clicks in the control window are excluded. Right clicks are unchanged. Generated input is ignored by the listener, preventing recursive clicking. Extra clicks follow the current cursor position; avoid moving the pointer to another control until the burst finishes. Drag-and-drop is not a supported trigger: releasing a drag outside the control window also schedules a burst. Rapid clicks queue bursts, up to 100 pending bursts; additional physical clicks still reach the target but do not add more queued work.

Windows may block generated clicks into apps running at a higher privilege level. Some games and other apps also reject simulated input. If F6 or F8 is already registered by another program, Multi Click reports it and exits; close the conflicting program and relaunch.

## Development and verification

The UI uses Python’s standard-library Tkinter. The Windows backend uses `WH_MOUSE_LL`, injected-input flags, `RegisterHotKey`, and `SendInput` through `ctypes`. The hook stays on its own message-loop thread and forwards work without blocking, following [Microsoft’s hook guidance](https://learn.microsoft.com/en-us/windows/win32/winmsg/lowlevelmouseproc).

Run the platform-independent engine tests and mocked Windows input-filter tests:

```sh
python -m unittest discover -s tests -v
```

Manual Windows check: open a disposable click counter, enable 5× and confirm one physical click gives five total events; repeat at 10×. At 100× with a long interval, press F8 partway through and confirm counting stops. Check that clicking the control window creates no extra clicks, F6 works while another app has focus, and closing the program cancels pending bursts. This repository was created in a Linux environment; actual Windows hook delivery and the desktop UI need this Windows smoke test.
