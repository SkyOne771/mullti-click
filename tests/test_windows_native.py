"""Native compatibility checks only; never inject mouse events."""

import ctypes
import sys
import unittest


@unittest.skipUnless(sys.platform == "win32", "Requires native Windows APIs")
class NativeWindowsTests(unittest.TestCase):
    def test_api_structures_match_windows_abi(self):
        from multiclick.windows import Input, MouseHookData

        is_64_bit = ctypes.sizeof(ctypes.c_void_p) == 8
        self.assertEqual(ctypes.sizeof(Input), 40 if is_64_bit else 28)
        self.assertEqual(ctypes.sizeof(MouseHookData), 32 if is_64_bit else 24)

    def test_tkinter_initializes(self):
        import tkinter

        root = tkinter.Tk()
        try:
            root.withdraw()
            root.update_idletasks()
            self.assertTrue(root.winfo_exists())
        finally:
            root.destroy()
