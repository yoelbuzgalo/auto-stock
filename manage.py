from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DEFAULT_VENV_DIR = ROOT / ".venv"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="manage.py",
        description="Auto Stock project helper.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a local virtual environment and install the project.")
    init_parser.add_argument("--venv", default=str(DEFAULT_VENV_DIR), help="Virtual environment directory.")
    init_parser.add_argument(
        "--force-reinstall",
        action="store_true",
        help="Run the editable install even if the virtual environment already exists.",
    )

    run_parser = subparsers.add_parser("run", help="Run the application through run.py.")
    run_parser.add_argument("args", nargs=argparse.REMAINDER, help="Arguments forwarded to run.py.")

    subparsers.add_parser("doctor", help="Show application health information.")
    subparsers.add_parser("gui", help="Launch the desktop application.")
    subparsers.add_parser("test", help="Run the test suite.")
    subparsers.add_parser("self-check", help="Run the project self-check.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        if args.command == "init":
            return run_init(Path(args.venv), force_reinstall=args.force_reinstall)
        if args.command == "run":
            return run_app(args.args)
        if args.command == "doctor":
            return run_app(["doctor"])
        if args.command == "gui":
            return run_app(["gui"])
        if args.command == "test":
            return run_tests()
        if args.command == "self-check":
            return run_self_check()
    except subprocess.CalledProcessError as exc:
        return exc.returncode

    parser.print_help()
    return 0


def run_init(venv_dir: Path, *, force_reinstall: bool) -> int:
    venv_existed = venv_dir.exists()
    python_executable = Path(sys.executable)
    using_virtualenv = False

    if venv_existed and not virtualenv_has_pip(venv_dir):
        print(f"Existing virtual environment in {venv_dir} is incomplete.")
        print("Removing it and trying again.")
        shutil.rmtree(venv_dir, ignore_errors=True)
        venv_existed = False

    if not venv_existed:
        print(f"Creating virtual environment in {venv_dir}...")
        try:
            run_command([sys.executable, "-m", "venv", str(venv_dir)])
        except subprocess.CalledProcessError:
            shutil.rmtree(venv_dir, ignore_errors=True)
            print("Virtual environment creation failed for this Python build.")
            print("Falling back to the current interpreter for initialization.")
        else:
            if virtualenv_has_pip(venv_dir):
                python_executable = venv_python(venv_dir)
                using_virtualenv = True
            else:
                shutil.rmtree(venv_dir, ignore_errors=True)
                print("Virtual environment was created without a working pip installation.")
                print("Falling back to the current interpreter for initialization.")
    else:
        if virtualenv_has_pip(venv_dir):
            print(f"Using existing virtual environment in {venv_dir}.")
            python_executable = venv_python(venv_dir)
            using_virtualenv = True
        else:
            print("Falling back to the current interpreter.")

    if force_reinstall or not venv_existed:
        print("Installing Auto Stock in editable mode...")
        temp_dir = ROOT / ".tmp_bootstrap"
        temp_dir.mkdir(exist_ok=True)
        try:
            run_command(
                [str(python_executable), "-m", "pip", "install", "-e", "."],
                cwd=ROOT,
                env=command_environment(temp_dir),
            )
        except subprocess.CalledProcessError:
            print("Editable install failed in this environment.")
            print("The repository is still runnable through `python manage.py run` from the repo root.")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    else:
        print("Editable install skipped. Use --force-reinstall to run it again.")

    env_file = ROOT / ".env"
    env_example = ROOT / ".env.example"
    if env_example.exists() and not env_file.exists():
        shutil.copy2(env_example, env_file)
        print("Created .env from .env.example.")
    elif env_file.exists():
        print("Keeping existing .env file.")

    print("Running self-check...")
    run_command([str(python_executable), "tools/self_check.py"], cwd=ROOT)

    print()
    print("Ready.")
    if using_virtualenv:
        print(f"Activate with: {activation_hint(venv_dir)}")
    else:
        print(f"Using interpreter: {python_executable}")
    print("Or run directly with: python manage.py run")
    return 0


def run_app(forwarded_args: list[str]) -> int:
    python_executable = preferred_python()
    return run_command([str(python_executable), "run.py", *forwarded_args], cwd=ROOT)


def run_tests() -> int:
    python_executable = preferred_python()
    return run_command([str(python_executable), "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=ROOT)


def run_self_check() -> int:
    python_executable = preferred_python()
    return run_command([str(python_executable), "tools/self_check.py"], cwd=ROOT)


def preferred_python() -> Path:
    if virtualenv_has_pip(DEFAULT_VENV_DIR):
        return venv_python(DEFAULT_VENV_DIR)
    return Path(sys.executable)


def venv_python(venv_dir: Path) -> Path:
    if sys.platform.startswith("win"):
        return venv_dir / "Scripts" / "python.exe"
    return venv_dir / "bin" / "python"


def activation_hint(venv_dir: Path) -> str:
    if sys.platform.startswith("win"):
        return str(venv_dir / "Scripts" / "Activate.ps1")
    return f"source {venv_dir / 'bin' / 'activate'}"


def virtualenv_has_pip(venv_dir: Path) -> bool:
    python_executable = venv_python(venv_dir)
    if not python_executable.exists():
        return False
    try:
        result = subprocess.run(
            [str(python_executable), "-c", "import pip"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return False
    return result.returncode == 0


def command_environment(temp_dir: Path) -> dict[str, str]:
    env = dict(os.environ)
    resolved = str(temp_dir)
    env["TMP"] = resolved
    env["TEMP"] = resolved
    env["TMPDIR"] = resolved
    return env


def run_command(command: list[str], *, cwd: Path | None = None, env: dict[str, str] | None = None) -> int:
    print("> " + " ".join(command))
    subprocess.run(command, cwd=cwd or ROOT, env=env, check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
