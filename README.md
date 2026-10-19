<img src="assets/icon.svg" width="64" height="64" alt="">

# Multi Click for Windows

[![CI](https://github.com/SkyOne771/mullti-click/actions/workflows/ci.yml/badge.svg)](https://github.com/SkyOne771/mullti-click/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D4)

A Windows desktop utility that turns one physical left click into 5, 10, or a custom number of total clicks in other applications. Built with Python, Tkinter, and the native Win32 API, with no third-party runtime dependencies.

**[Download current source](https://github.com/SkyOne771/mullti-click/archive/refs/heads/main.zip)** · **[Automated checks and packaged builds](https://github.com/SkyOne771/mullti-click/actions/workflows/ci.yml)** · **[Report an issue](https://github.com/SkyOne771/mullti-click/issues)**

## Features

- One-click presets and custom multipliers from 2 to 100 total clicks.
- Adjustable click spacing, global keyboard shortcuts, and session counters.
- Starts paused; stopping or closing the app cancels pending work.
- Filters injected input to prevent recursive click multiplication.
- Excludes physical clicks inside the control window.
- Separates native input handling, thread-safe scheduling, and desktop controls.

## Run

1. On **Windows 10 or 11**, install **Python 3.10 or newer** from [python.org](https://www.python.org/downloads/windows/). Keep the installer’s **Tcl/Tk and IDLE** option enabled.
2. [Download the current source ZIP](https://github.com/SkyOne771/mullti-click/archive/refs/heads/main.zip) and extract it on your Windows computer.
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

Clone the project and run the tests; no pip installation is required:

```sh
git clone https://github.com/SkyOne771/mullti-click.git
cd mullti-click
python -m unittest discover -s tests -v
```

The suite covers exact click counts, queued bursts, cancellation, invalid settings, injection failures, and input filtering. Native Windows checks additionally verify API structure sizes and that Tkinter initializes. CI runs on Windows and Linux with Python 3.10 and 3.13 for every push and pull request. These checks do not generate system clicks.

Build a distributable source ZIP locally:

```sh
python tools/package.py
```

The result is `dist/MultiClick-Windows.zip`; Python is still required to run it. Successful CI runs also publish a source ZIP artifact named with its commit SHA, available from the run page while GitHub retains it. The download link above always points to the current `main` branch. Changes must be committed and pushed to reach GitHub; CI does not upload uncommitted local files.

### Architecture

| File | Responsibility |
| --- | --- |
| `multiclick/engine.py` | Condition-based worker queue, configuration, counters, cancellation, and error handling |
| `multiclick/windows.py` | Low-level mouse hook, injected-input filtering, global hotkeys, and native click injection |
| `multiclick/ui.py` | Tkinter controls and event dispatch between the UI and input listener |
| `tests/` | Scheduling, filtering, and Windows-native compatibility checks |
| `tools/package.py` | Source ZIP packaging from an explicit set of project files |

The hook thread forwards physical clicks and hotkeys to the UI through a queue. The UI schedules extra clicks on the engine worker, keeping native hook callbacks short. Each burst snapshots the multiplier and interval. A cancellation generation invalidates current and queued bursts when paused.

### Manual Windows verification

Actual mouse delivery into another application still needs a manual check on Windows:

1. Open a disposable click counter, enable 5×, and confirm one physical click produces five total events. Repeat at 10×.
2. At 100× with a long interval, press F8 partway through and confirm counting stops.
3. Check that physical clicks in the control window create no extra clicks.
4. Check F6 while another app has focus and close the utility during a burst to verify cancellation.

## Project notes

This project demonstrates Python desktop development, Win32 API integration through `ctypes`, concurrency, event-driven design, and automated testing. End-to-end input behavior has not yet been manually verified on Windows; the automated checks and their limits are described above.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the development workflow and [CHANGELOG.md](CHANGELOG.md) for changes.
