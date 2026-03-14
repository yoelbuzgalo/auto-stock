from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    pyinstaller = shutil.which("pyinstaller")
    if pyinstaller is None:
        print("PyInstaller is not installed. Run `python -m pip install .[build]` first.")
        return 1

    command = [
        pyinstaller,
        "--noconfirm",
        "--clean",
        "--windowed",
        "--name",
        "AutoStock",
        "--collect-submodules",
        "auto_stock",
        str(root / "run.py"),
    ]
    subprocess.run(command, cwd=root, check=True)
    print("Desktop build created in the dist directory.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
