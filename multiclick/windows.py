"""Windows mouse hooks and SendInput; no third-party dependencies."""

import ctypes as C
from ctypes import wintypes as W
import threading

user32 = C.WinDLL("user32", use_last_error=True)
kernel32 = C.WinDLL("kernel32", use_last_error=True)
ULONG_PTR = W.WPARAM
LRESULT = C.c_ssize_t
HOOKPROC = C.WINFUNCTYPE(LRESULT, C.c_int, W.WPARAM, W.LPARAM)


class MouseHookData(C.Structure):
    _fields_ = [("pt", W.POINT), ("mouseData", W.DWORD),
                ("flags", W.DWORD), ("time", W.DWORD), ("extra", ULONG_PTR)]


class MouseInput(C.Structure):
    _fields_ = [("dx", W.LONG), ("dy", W.LONG), ("mouseData", W.DWORD),
                ("flags", W.DWORD), ("time", W.DWORD), ("extra", ULONG_PTR)]


class KeyboardInput(C.Structure):
    _fields_ = [("vk", W.WORD), ("scan", W.WORD), ("flags", W.DWORD),
                ("time", W.DWORD), ("extra", ULONG_PTR)]


class HardwareInput(C.Structure):
    _fields_ = [("message", W.DWORD), ("low", W.WORD), ("high", W.WORD)]


class InputUnion(C.Union):
    _fields_ = [("mouse", MouseInput), ("keyboard", KeyboardInput),
                ("hardware", HardwareInput)]


class Input(C.Structure):
    _fields_ = [("type", W.DWORD), ("data", InputUnion)]


user32.SetWindowsHookExW.argtypes = [C.c_int, HOOKPROC, W.HINSTANCE, W.DWORD]
user32.SetWindowsHookExW.restype = W.HANDLE
user32.CallNextHookEx.argtypes = [W.HANDLE, C.c_int, W.WPARAM, W.LPARAM]
user32.CallNextHookEx.restype = LRESULT
user32.UnhookWindowsHookEx.argtypes = [W.HANDLE]
user32.UnhookWindowsHookEx.restype = W.BOOL
user32.SendInput.argtypes = [W.UINT, C.POINTER(Input), C.c_int]
user32.SendInput.restype = W.UINT
user32.WindowFromPoint.argtypes = [W.POINT]
user32.WindowFromPoint.restype = W.HWND
user32.GetAncestor.argtypes = [W.HWND, W.UINT]
user32.GetAncestor.restype = W.HWND
user32.RegisterHotKey.argtypes = [W.HWND, C.c_int, W.UINT, W.UINT]
user32.RegisterHotKey.restype = W.BOOL
user32.UnregisterHotKey.argtypes = [W.HWND, C.c_int]
user32.GetMessageW.argtypes = [C.POINTER(W.MSG), W.HWND, W.UINT, W.UINT]
user32.GetMessageW.restype = W.BOOL
user32.PostThreadMessageW.argtypes = [W.DWORD, W.UINT, W.WPARAM, W.LPARAM]
user32.PostThreadMessageW.restype = W.BOOL
kernel32.GetCurrentThreadId.restype = W.DWORD
kernel32.GetModuleHandleW.argtypes = [W.LPCWSTR]
kernel32.GetModuleHandleW.restype = W.HMODULE


def send_click():
    inputs = (Input * 2)()
    inputs[0].data.mouse.flags = 0x0002  # LEFTDOWN
    inputs[1].data.mouse.flags = 0x0004  # LEFTUP
    if user32.SendInput(2, inputs, C.sizeof(Input)) != 2:
        # Best effort release if Windows accepted only the down event.
        user32.SendInput(1, C.byref(inputs[1]), C.sizeof(Input))
        raise RuntimeError("Windows blocked a click. The target may be running as administrator.")


class WindowsBackend:
    def __init__(self, own_window, on_event):
        self.own_window = own_window
        self.on_event = on_event
        self.thread_id = None
        self.error = None
        self._ready = threading.Event()
        self._callback = HOOKPROC(self._mouse_event)
        self._thread = threading.Thread(target=self._listen, daemon=True, name="windows-hooks")

    def start(self):
        self._thread.start()
        if not self._ready.wait(5):
            raise RuntimeError("Windows input listener did not start.")
        if self.error:
            raise RuntimeError(self.error)

    def _mouse_event(self, code, message, pointer):
        if code >= 0 and message == 0x0202:  # WM_LBUTTONUP
            event = C.cast(pointer, C.POINTER(MouseHookData)).contents
            # Windows marks generated input: never multiply it again.
            if not event.flags & 0x01:
                target = user32.GetAncestor(user32.WindowFromPoint(event.pt), 2)
                if target != self.own_window:
                    # SendInput waits for the hook, so never block this thread.
                    self.on_event("click")
        return user32.CallNextHookEx(None, code, message, pointer)

    def _listen(self):
        self.thread_id = kernel32.GetCurrentThreadId()
        hook = None
        registered = []
        try:
            hook = user32.SetWindowsHookExW(14, self._callback, kernel32.GetModuleHandleW(None), 0)
            if not hook:
                raise C.WinError(C.get_last_error())
            for key_id, key in [(1, 0x75), (2, 0x77)]:  # F6, F8
                if not user32.RegisterHotKey(None, key_id, 0x4000, key):
                    raise RuntimeError("F6 or F8 is already used by another app. Close it and restart Multi Click.")
                registered.append(key_id)
            self._ready.set()
            message = W.MSG()
            while True:
                result = user32.GetMessageW(C.byref(message), None, 0, 0)
                if result == 0:
                    break
                if result == -1:
                    raise C.WinError(C.get_last_error())
                if message.message == 0x0312:  # WM_HOTKEY
                    self.on_event("stop" if message.wParam == 2 else "toggle")
        except Exception as exc:
            self.error = str(exc)
            self.on_event("stop")
        finally:
            self._ready.set()
            for key_id in registered:
                user32.UnregisterHotKey(None, key_id)
            if hook:
                user32.UnhookWindowsHookEx(hook)

    def close(self):
        if self.thread_id:
            user32.PostThreadMessageW(self.thread_id, 0x0012, 0, 0)
        self._thread.join(timeout=2)
