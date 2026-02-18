# Samsung MDC Control (Async)

## Setup

1. Open this folder in VS Code.
2. (Optional) Create and activate a virtual environment.
3. Install dependencies:

```bash
py -m pip install -r requirements.txt
```

## CLI script

Edit `IP_ADDRESS` in `screen_control.py` or pass it from CLI.

Run default flow (status + screenshot):

```bash
py screen_control.py
```

Examples:

```bash
py screen_control.py --ip 192.168.1.50 --id 0
py screen_control.py --ip 192.168.1.50 --brightness 80
py screen_control.py --ip 192.168.1.50 --reboot
py screen_control.py --ip 192.168.1.50 --no-screenshot
```

## Desktop dashboard (CustomTkinter)

Run directly:

```bash
py launch_dashboard.py
```

This gives you buttons for status, reboot, volume, input source, mute, brightness, serial number, and `KEY_CONTENT` (Home equivalent).

## Build EXE (Windows, Nuitka)

Install build dependencies:

```bash
py -m pip install -U nuitka zstandard ordered-set
```

Build single-file EXE:

```bash
py -m nuitka --onefile --standalone --windows-console-mode=disable --output-filename=SamsungMDCDashboard.exe launch_dashboard.py
```

Output EXE is created in the Nuitka output folder shown in terminal.

## Build Installer (optional)

If you want a setup wizard (`.exe` installer), create the EXE first with Nuitka, then package it with your installer tool of choice (for example Inno Setup).
