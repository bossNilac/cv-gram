import argparse
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
FRONTEND_DIR = ROOT / "frontend" / "CV_GRAM"
FRONTEND_DIST_DIR = FRONTEND_DIR / "dist"
BACKEND_FRONTEND_DIR = ROOT / "backend" / "static" / "frontend"


def run(command: list[str], cwd: Path) -> None:
    executable = shutil.which(command[0])
    if executable is None and sys.platform.startswith("win") and not command[0].lower().endswith(".cmd"):
        executable = shutil.which(f"{command[0]}.cmd")
    if executable is None:
        raise SystemExit(f"Required command not found: {command[0]}")

    resolved_command = [executable, *command[1:]]
    completed = subprocess.run(resolved_command, cwd=cwd, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def build_frontend() -> None:
    if not FRONTEND_DIR.exists():
        raise SystemExit(f"Frontend directory not found: {FRONTEND_DIR}")

    run(["npm", "run", "build"], FRONTEND_DIR)

    if BACKEND_FRONTEND_DIR.exists():
        shutil.rmtree(BACKEND_FRONTEND_DIR)

    BACKEND_FRONTEND_DIR.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(FRONTEND_DIST_DIR, BACKEND_FRONTEND_DIR)


def start_backend(host: str, port: int, reload_enabled: bool) -> None:
    command = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.main:app",
        "--host",
        host,
        "--port",
        str(port),
    ]
    if reload_enabled:
        command.append("--reload")

    run(command, ROOT)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build the CV_GRAM frontend into the backend and run the app on one port."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--reload", action="store_true")
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="Run the backend without rebuilding/copying the frontend bundle.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.skip_build:
        build_frontend()
    start_backend(args.host, args.port, args.reload)


if __name__ == "__main__":
    main()
