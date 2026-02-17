import asyncio
import shlex
import socket
import subprocess
import sys
import time
from pathlib import Path

import streamlit as st
from samsung_mdc import MDC

ALL_CLI_COMMANDS = sorted(MDC._commands.keys())

st.set_page_config(page_title="Samsung Screen Control", page_icon="🖥️", layout="centered")
st.title("Samsung MDC Dashboard")

ip_address = st.text_input("IP Address", value="192.168.1.50")
port = st.number_input("Port", min_value=1, max_value=65535, value=1515, step=1)
display_id = st.number_input("Display ID", min_value=0, max_value=255, value=0, step=1)

target = f"{ip_address}:{port}"


def check_network_reachability(host: str, tcp_port: int, timeout: float = 1.5):
    start_time = time.perf_counter()
    try:
        with socket.create_connection((host, int(tcp_port)), timeout=timeout):
            elapsed_ms = int((time.perf_counter() - start_time) * 1000)
            return True, f"Reachable in {elapsed_ms} ms"
    except OSError as exc:
        return False, str(exc)


def render_network_light(host: str, tcp_port: int):
    online, details = check_network_reachability(host, tcp_port)
    light = "🟢" if online else "🔴"
    state = "ONLINE" if online else "OFFLINE"
    st.markdown(f"**TV Network:** {light} {state}")
    st.caption(f"Checking {host}:{tcp_port} every 10s • {details}")


if hasattr(st, "fragment"):
    @st.fragment(run_every="10s")
    def network_light_fragment():
        render_network_light(ip_address, int(port))

    network_light_fragment()
else:
    render_network_light(ip_address, int(port))


POWER_MAP = {
    0: "OFF",
    1: "ON",
    2: "REBOOT",
}

MUTE_MAP = {
    0: "OFF",
    1: "ON",
    255: "UNAVAILABLE",
}

INPUT_SOURCE_MAP = {
    0x18: "DVI",
    0x21: "HDMI1",
    0x23: "HDMI2",
    0x25: "DISPLAY_PORT_1",
    0x31: "HDMI3",
    0x33: "HDMI4",
}

PICTURE_ASPECT_MAP = {
    0x10: "PC_16_9",
    0x18: "PC_4_3",
    0x20: "PC_ORIGINAL_RATIO",
    0x01: "VIDEO_16_9",
    0x0B: "VIDEO_4_3",
}


def _label(code, mapping):
    if code is None:
        return "UNKNOWN"
    return mapping.get(int(code), f"UNKNOWN ({code})")


def decode_status(raw_status):
    values = list(raw_status)

    power = values[0] if len(values) > 0 else None
    volume = values[1] if len(values) > 1 else None
    mute = values[2] if len(values) > 2 else None
    input_source = values[3] if len(values) > 3 else None
    picture_aspect = values[4] if len(values) > 4 else None
    n_time_nf = values[5] if len(values) > 5 else None
    f_time_nf = values[6] if len(values) > 6 else None

    return {
        "power": _label(power, POWER_MAP),
        "volume": volume,
        "mute": _label(mute, MUTE_MAP),
        "input_source": _label(input_source, INPUT_SOURCE_MAP),
        "picture_aspect": _label(picture_aspect, PICTURE_ASPECT_MAP),
        "n_time_nf": n_time_nf,
        "f_time_nf": f_time_nf,
    }


def diagnose_status_error(exc: Exception):
    message = str(exc)
    lower = message.lower()

    if "response header read timeout" in lower:
        return (
            "TV network is reachable, but MDC did not answer status. "
            "Possible causes: wrong Display ID, panel in deep standby, or Secured Protocol PIN required."
        )
    if "connect timeout" in lower:
        return "Cannot reach TV MDC service on network. Check IP/port/firewall and network path."
    if "nak" in lower:
        return "TV rejected command (NAK). Check model support, current input state, and command compatibility."
    return message


def probe_common_display_ids(ip: str, tcp_port: int, ids=(0, 1)):
    results = []
    target_to_probe = f"{ip}:{int(tcp_port)}"

    async def _probe(id_to_try: int):
        async with MDC(target_to_probe) as mdc:
            return await mdc.status(id_to_try)

    for id_to_try in ids:
        try:
            _ = run_async(_probe(id_to_try))
            results.append((id_to_try, True, "OK"))
        except Exception as probe_exc:
            results.append((id_to_try, False, str(probe_exc)))
    return results


async def mdc_call(coro):
    async with MDC(target) as mdc:
        return await coro(mdc)


def run_async(coro):
    return asyncio.run(coro)


def get_command_argument_options(command_name: str):
    command = MDC._commands.get(command_name)
    if not command:
        return []

    data_fields = getattr(command, "DATA", [])
    if len(data_fields) != 1:
        return []

    field = data_fields[0]
    if hasattr(field, "enum") and getattr(field, "enum") is not None:
        return [member.name for member in field.enum]

    return []


col1, col2 = st.columns(2)

if col1.button("Get Status", use_container_width=True):
    try:
        status = run_async(mdc_call(lambda mdc: mdc.status(display_id)))
        decoded_status = decode_status(status)
        st.success("Status fetched")
        st.json(decoded_status)
        with st.expander("Show raw status values"):
            st.json(status)
    except Exception as exc:
        st.error(diagnose_status_error(exc))

        with st.expander("Troubleshooting details"):
            st.write(f"Selected Display ID: {display_id}")
            st.write(f"Raw error: {exc}")

            probe_results = probe_common_display_ids(ip_address, int(port), ids=(0, 1))
            probe_summary = {
                f"id_{id_to_try}": "OK" if ok else f"Fail: {err}"
                for id_to_try, ok, err in probe_results
            }
            st.json(probe_summary)

if col2.button("Reboot", use_container_width=True):
    try:
        run_async(mdc_call(lambda mdc: mdc.power(display_id, ("REBOOT",))))
        st.success("Reboot command sent")
    except Exception as exc:
        st.error(str(exc))

if st.button("Capture Screenshot", use_container_width=True):
    try:
        def do_capture(mdc):
            if not hasattr(mdc, "screen_capture"):
                raise RuntimeError(
                    "Screenshot is not supported by this installed python-samsung-mdc version/device."
                )
            return mdc.screen_capture(display_id)

        image_data = run_async(mdc_call(do_capture))
        output_path = Path("screen_view.jpg")
        output_path.write_bytes(image_data)
        st.success(f"Saved screenshot to {output_path}")
        st.image(image_data, caption="Live Screen View")
    except Exception as exc:
        st.error(str(exc))

st.subheader("Quick Controls")

volume = st.slider("Volume", min_value=0, max_value=100, value=25)
if st.button("Set Volume", use_container_width=True):
    try:
        run_async(mdc_call(lambda mdc: mdc.volume(display_id, (volume,))))
        st.success(f"Volume set to {volume}")
    except Exception as exc:
        st.error(str(exc))

source_labels = {
    "HDMI 1": "HDMI1",
    "HDMI 2": "HDMI2",
    "DVI": "DVI",
    "DisplayPort 1": "DISPLAY_PORT_1",
}
source_label = st.selectbox("Input Source", options=list(source_labels.keys()))
source = source_labels[source_label]
if st.button("Set Input", use_container_width=True):
    try:
        run_async(mdc_call(lambda mdc: mdc.input_source(display_id, (source,))))
        st.success(f"Input set to {source_label}")
    except Exception as exc:
        st.error(str(exc))

mute_state = st.selectbox("Mute", options=["ON", "OFF"])
if st.button("Set Mute", use_container_width=True):
    try:
        run_async(mdc_call(lambda mdc: mdc.mute(display_id, (mute_state,))))
        st.success(f"Mute set to {mute_state}")
    except Exception as exc:
        st.error(str(exc))

brightness = st.slider("Brightness", min_value=0, max_value=100, value=80)
if st.button("Set Brightness", use_container_width=True):
    try:
        run_async(mdc_call(lambda mdc: mdc.brightness(display_id, (brightness,))))
        st.success(f"Brightness set to {brightness}")
    except Exception as exc:
        st.error(str(exc))

if st.button("Get Serial Number", use_container_width=True):
    try:
        serial = run_async(mdc_call(lambda mdc: mdc.serial_number(display_id)))
        st.info(f"Serial: {serial}")
    except Exception as exc:
        st.error(str(exc))

if st.button("Remote: Home (KEY_CONTENT)", use_container_width=True):
    try:
        run_async(mdc_call(lambda mdc: mdc.virtual_remote(display_id, ("KEY_CONTENT",))))
        st.success("Sent KEY_CONTENT")
    except Exception as exc:
        st.error(str(exc))

st.subheader("Advanced CLI Command")
st.caption("Choose a command, then optionally add arguments (example args: on, HDMI1, KEY_CONTENT)")

selected_command = st.selectbox("CLI Command", options=ALL_CLI_COMMANDS, index=ALL_CLI_COMMANDS.index("status") if "status" in ALL_CLI_COMMANDS else 0)

argument_options = get_command_argument_options(selected_command)
selected_argument_option = st.selectbox(
    "Argument Dropdown",
    options=["(none)", *argument_options],
    index=0,
)
command_args = st.text_input("Arguments (optional)", value="")

if st.button("Run Advanced Command", use_container_width=True):
    try:
        effective_args = command_args.strip()
        if not effective_args and selected_argument_option != "(none)":
            effective_args = selected_argument_option

        parsed_args = shlex.split(effective_args) if effective_args else []
        cli_target = f"{display_id}@{ip_address}:{int(port)}"
        cli_cmd = [sys.executable, "-m", "samsung_mdc", cli_target, selected_command, *parsed_args]
        result = subprocess.run(
            cli_cmd,
            capture_output=True,
            text=True,
            timeout=25,
            check=False,
        )

        if result.returncode == 0:
            st.success("Command executed")
        else:
            st.error(f"Command failed (exit code {result.returncode})")

        if result.stdout.strip():
            st.text_area("Output", value=result.stdout, height=160)

        if result.stderr.strip():
            st.text_area("Errors", value=result.stderr, height=120)
    except Exception as exc:
        st.error(str(exc))
