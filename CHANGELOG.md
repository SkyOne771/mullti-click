# Changelog

## Unreleased

- Updated the README to reflect the owner's successful Windows test reported on 2026-10-27.
- Added a portfolio-focused README, architecture notes, and contribution instructions.
- Added CI for Windows and Linux on Python 3.10 and 3.13.
- Added native Windows structure and Tkinter initialization checks without generating mouse input.
- Added source ZIP packaging and commit-specific CI artifacts.

## Initial implementation — 2026-10-18

- Windows desktop controls with 2×, 5×, 10×, and 20× presets and custom counts from 2 to 100.
- Configurable spacing from 10 to 1000 ms, global F6/F8 shortcuts, and session counters.
- Native Windows mouse hook and click injection with generated-input filtering.
- Thread-safe queued bursts, cancellation, and control-window exclusion.
- Thirteen automated engine and mocked input tests.
