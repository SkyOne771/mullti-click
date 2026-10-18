import sys


def main():
    if sys.platform != "win32":
        print("Multi Click runs on Windows 10/11. Copy this folder to Windows and run start.bat.")
        return 1
    from .ui import run
    run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
