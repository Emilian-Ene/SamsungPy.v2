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

## Web dashboard

Run directly (auto-opens your default web browser):

```bash
py launch_dashboard.py
```

If port `8501` is already in use, the launcher automatically selects a free localhost port.

Alternative manual run:

```bash
py -m streamlit run dashboard.py
```

VS Code task:

- Run `Terminal > Run Task > Launch Samsung Dashboard`.

This gives you buttons for status, reboot, volume, input source, mute, brightness, serial number, and `KEY_CONTENT` (Home equivalent).

## Build EXE (Windows)

Create a standalone Windows app folder:

```bash
build_exe.bat
```

Output:

- `dist\SamsungMDCDashboard\SamsungMDCDashboard.exe`

You can copy the full `dist\SamsungMDCDashboard` folder to another PC and run the EXE.

## Build Installer (optional)

If you want a setup wizard (`.exe` installer):

1. Install **Inno Setup**.
2. Open `installer_inno_setup.iss`.
3. Click **Build**.

Output installer:

- `installer\SamsungMDCDashboard-Setup.exe`
