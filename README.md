## Local loopback multiplayer debug test

Run this command from the repository root:

```bash
python scripts/debug_loopback_multiplayer.py
```

Expected behavior:
- The launcher picks a random free localhost TCP port.
- Two game processes are started: host first, then client.
- You should see two game windows (host + client), with console logs prefixed by `[HOST]` and `[CLIENT]`.
- Press `Ctrl+C` in the launcher terminal to terminate both processes cleanly.

Troubleshooting:
- **Port in use:** rerun the command; it auto-selects another free port each run.
- **Firewall/network prompts:** allow localhost (`127.0.0.1`) traffic for Python if prompted.
- **Stale process/windows:** close leftover game windows and rerun; if needed, manually terminate old Python processes.
