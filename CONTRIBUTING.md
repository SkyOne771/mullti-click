# Contributing

## Setup

Use Python 3.10 or newer. The app requires Windows 10/11 and Python's Tcl/Tk component. Engine and mocked backend tests also run on Linux. No third-party packages are required.

```sh
git clone https://github.com/SkyOne771/mullti-click.git
cd mullti-click
python -m unittest discover -s tests -v
python -m compileall -q multiclick tests tools
python tools/package.py
```

On Windows, launch with `py -3 -m multiclick` or `start.bat`.

## Changes

1. Keep input hooks short and nonblocking. Never perform click injection or acquire the engine's lock in a hook callback.
2. Preserve filtering of injected input, control-window exclusion, paused startup, and cancellation when stopping or closing.
3. Add tests for changed behavior. Tests must not generate system-wide mouse input.
4. Update the README when controls, requirements, behavior, or limitations change. Record user-visible changes under **Unreleased** in the changelog.
5. Run tests, compilation, packaging, and `git diff --check` before submitting a pull request.

For native input changes, follow the manual Windows verification steps in the README and report what was actually checked. Passing mocked tests does not establish that input reaches every application.

## Publishing updates

The public repository tracks pushed commits, not local file edits. Push completed changes to your branch and open a pull request; maintainers may push authorized updates directly to `main`. CI runs on every push and pull request, then builds a source ZIP after its tests pass. The README download link follows `main`, so it reflects changes once they reach that branch. Downloads still require Python; the ZIP is not a standalone executable.

File bug reports through GitHub Issues with the Windows and Python versions, multiplier and interval settings, target application, expected result, and actual result. Avoid including private application data.
