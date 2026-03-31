"""Debug helper to launch loopback host/client multiplayer processes.

Usage:
    python scripts/debug_loopback_multiplayer.py
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import threading
import time
from pathlib import Path


def _find_free_local_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


def _stream_output(prefix: str, stream) -> None:
    for line in iter(stream.readline, ""):
        print(f"{prefix} {line.rstrip()}")


def _spawn_game_process(mode: str, player_index: int, host_ip: str, host_port: int) -> subprocess.Popen:
    env = os.environ.copy()
    env.update(
        {
            "NETWORK_MODE": mode,
            "HOST_IP": host_ip,
            "HOST_PORT": str(host_port),
            "PLAYER_INDEX": str(player_index),
            # Optional: flip to "1" here if you want extra in-game debug signals.
            "DEBUG": env.get("DEBUG", "0"),
        }
    )

    repo_root = Path(__file__).resolve().parents[1]
    return subprocess.Popen(
        [sys.executable, "run_game.py"],
        cwd=repo_root,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


def _terminate_process(process: subprocess.Popen | None) -> None:
    if process is None or process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        process.kill()


def main() -> int:
    host_ip = "127.0.0.1"
    host_port = _find_free_local_port()

    print(f"[LAUNCHER] Starting loopback multiplayer test on {host_ip}:{host_port}")
    print("[LAUNCHER] Starting host process first...")
    host = _spawn_game_process("host", 0, host_ip, host_port)

    host_log_thread = threading.Thread(
        target=_stream_output,
        args=("[HOST]", host.stdout),
        daemon=True,
    )
    host_log_thread.start()

    time.sleep(1.5)

    print("[LAUNCHER] Starting client process...")
    client = _spawn_game_process("client", 1, host_ip, host_port)
    client_log_thread = threading.Thread(
        target=_stream_output,
        args=("[CLIENT]", client.stdout),
        daemon=True,
    )
    client_log_thread.start()

    try:
        while True:
            if host.poll() is not None:
                print("[LAUNCHER] Host exited; shutting down client.")
                break
            if client.poll() is not None:
                print("[LAUNCHER] Client exited; shutting down host.")
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\n[LAUNCHER] Ctrl+C detected; shutting down host/client...")
    finally:
        _terminate_process(host)
        _terminate_process(client)

    return 0


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.default_int_handler)
    raise SystemExit(main())
