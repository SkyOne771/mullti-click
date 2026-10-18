"""Exercise hook filtering with mocked APIs, without generating OS input."""

import ctypes
import importlib.util
from pathlib import Path
import unittest
from unittest.mock import MagicMock, patch


class WindowsBackendTests(unittest.TestCase):
    def setUp(self):
        self.api = MagicMock()
        path = Path(__file__).resolve().parents[1] / "multiclick" / "windows.py"
        spec = importlib.util.spec_from_file_location("windows_under_test", path)
        self.module = importlib.util.module_from_spec(spec)
        with patch.object(ctypes, "WinDLL", return_value=self.api, create=True), \
             patch.object(ctypes, "WINFUNCTYPE", ctypes.CFUNCTYPE, create=True):
            spec.loader.exec_module(self.module)
        self.events = []
        self.backend = self.module.WindowsBackend(100, self.events.append)
        self.api.GetAncestor.return_value = 200
        self.api.CallNextHookEx.return_value = 123

    def dispatch(self, flags=0, code=0, message=0x0202):
        event = self.module.MouseHookData()
        event.flags = flags
        result = self.backend._mouse_event(code, message, ctypes.addressof(event))
        self.assertEqual(result, 123)

    def test_physical_left_release_is_forwarded_once(self):
        self.dispatch()
        self.assertEqual(self.events, ["click"])

    def test_generated_clicks_never_recurse(self):
        self.dispatch(flags=1)
        self.dispatch(flags=3)
        self.assertEqual(self.events, [])

    def test_control_window_is_excluded(self):
        self.api.GetAncestor.return_value = 100
        self.dispatch()
        self.assertEqual(self.events, [])

    def test_right_click_and_negative_hook_codes_are_ignored(self):
        self.dispatch(message=0x0205)
        self.dispatch(code=-1)
        self.assertEqual(self.events, [])

    def test_injected_pair_contains_left_down_and_left_up(self):
        observed = []

        def record(count, inputs, size):
            observed.extend(inputs[index].data.mouse.flags for index in range(count))
            return count

        self.api.SendInput.side_effect = record
        self.module.send_click()
        self.assertEqual(observed, [0x0002, 0x0004])

    def test_failed_injection_tries_release_and_reports_error(self):
        self.api.SendInput.side_effect = [0, 1]
        with self.assertRaisesRegex(RuntimeError, "Windows blocked"):
            self.module.send_click()
        self.assertEqual(self.api.SendInput.call_count, 2)
