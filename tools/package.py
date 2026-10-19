"""Build the Windows source distribution without third-party tools."""

from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


def build():
    root = Path(__file__).resolve().parents[1]
    output = root / "dist" / "MultiClick-Windows.zip"
    output.parent.mkdir(exist_ok=True)
    files = [root / name for name in (
        "README.md", "CONTRIBUTING.md", "CHANGELOG.md", "start.bat", ".gitignore",
    )]
    for directory, pattern in (("multiclick", "*.py"), ("tests", "*.py"),
                               ("tools", "*.py"), ("assets", "*.svg")):
        files.extend(sorted((root / directory).glob(pattern)))
    with ZipFile(output, "w", ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, Path("MultiClick") / path.relative_to(root))
    with ZipFile(output) as archive:
        if archive.testzip() is not None:
            raise RuntimeError("Source archive failed verification")
    print(f"Created {output} ({len(files)} files)")
    return output


if __name__ == "__main__":
    build()
