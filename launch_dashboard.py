import os
os.environ["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"

import sys
import socket
from pathlib import Path

from streamlit.web import bootstrap


def find_free_port(preferred_port: int = 8501) -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if sock.connect_ex(("127.0.0.1", preferred_port)) != 0:
            return preferred_port

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> None:
    if getattr(sys, "frozen", False):
        # When running as a PyInstaller bundle, use the temp extraction folder
        base_dir = Path(getattr(sys, '_MEIPASS', Path(sys.executable).resolve().parent))
    else:
        base_dir = Path(__file__).resolve().parent
    dashboard_file = base_dir / "dashboard.py"
    if not dashboard_file.exists():
        raise FileNotFoundError(f"dashboard.py not found in {base_dir}")

    port = find_free_port(8501)
    bootstrap.run(
        str(dashboard_file),
        False,
        [],
        {
            "server.headless": False,
            "server.address": "127.0.0.1",
            "server.port": port,
            "browser.serverAddress": "127.0.0.1",
            "browser.gatherUsageStats": False,
            "server.runOnSave": False,
        },
    )


if __name__ == "__main__":
    main()
