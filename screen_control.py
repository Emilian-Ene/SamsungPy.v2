import argparse
import asyncio
from pathlib import Path

from samsung_mdc import MDC

# --- CONFIGURATION ---
IP_ADDRESS = "192.168.1.50"  # <--- PUT YOUR SCREEN IP HERE
DISPLAY_ID = 0  # Default is 0 for most QMRE screens
PORT = 1515
OUTPUT_IMAGE = Path("screen_view.jpg")


def build_target(ip_address: str, port: int) -> str:
    return f"{ip_address}:{port}"


async def get_status(mdc: MDC, display_id: int) -> tuple:
    return await mdc.status(display_id)


async def capture_screen(mdc: MDC, display_id: int, output_path: Path = OUTPUT_IMAGE) -> Path:
    if not hasattr(mdc, "screen_capture"):
        raise RuntimeError(
            "Screenshot is not supported by this installed python-samsung-mdc version/device."
        )
    image_data = await mdc.screen_capture(display_id)
    output_path.write_bytes(image_data)
    return output_path


async def reboot_screen(mdc: MDC, display_id: int) -> None:
    await mdc.power(display_id, ("REBOOT",))


async def set_brightness(mdc: MDC, display_id: int, value: int) -> None:
    await mdc.brightness(display_id, (value,))


async def set_volume(mdc: MDC, display_id: int, value: int) -> None:
    await mdc.volume(display_id, (value,))


async def set_input_source(mdc: MDC, display_id: int, source: str) -> None:
    await mdc.input_source(display_id, (source,))


async def set_mute(mdc: MDC, display_id: int, state: str) -> None:
    await mdc.mute(display_id, (state,))


async def get_serial_number(mdc: MDC, display_id: int):
    return await mdc.serial_number(display_id)


async def press_remote_key(mdc: MDC, display_id: int, key: str) -> None:
    await mdc.virtual_remote(display_id, (key,))


async def run_commands(
    ip_address: str,
    port: int,
    display_id: int,
    do_screenshot: bool = True,
    do_reboot: bool = False,
    brightness: int | None = None,
) -> None:
    target = build_target(ip_address, port)

    async with MDC(target) as mdc:
        print(f"--- Connecting to {ip_address} ---")

        status = await get_status(mdc, display_id)
        power_value = status[0] if len(status) > 0 else "UNKNOWN"
        volume_value = status[1] if len(status) > 1 else "UNKNOWN"
        print(f"Current Power: {power_value}")
        print(f"Current Volume: {volume_value}")

        if do_screenshot:
            print("Capturing screen...")
            try:
                saved_to = await capture_screen(mdc, display_id)
                print(f"Screenshot saved as '{saved_to.name}'")
            except RuntimeError as exc:
                print(exc)

        if brightness is not None:
            await set_brightness(mdc, display_id, brightness)
            print(f"Brightness set to {brightness}.")

        if do_reboot:
            await reboot_screen(mdc, display_id)
            print("Reboot command sent.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Samsung MDC async controller")
    parser.add_argument("--ip", default=IP_ADDRESS, help="Screen IP address")
    parser.add_argument("--port", type=int, default=PORT, help="MDC TCP port")
    parser.add_argument("--id", type=int, default=DISPLAY_ID, help="Display ID")
    parser.add_argument(
        "--no-screenshot",
        action="store_true",
        help="Skip screenshot capture",
    )
    parser.add_argument(
        "--reboot",
        action="store_true",
        help="Send reboot command",
    )
    parser.add_argument(
        "--brightness",
        type=int,
        default=None,
        help="Brightness value (0-100)",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    try:
        asyncio.run(
            run_commands(
                ip_address=args.ip,
                port=args.port,
                display_id=args.id,
                do_screenshot=not args.no_screenshot,
                do_reboot=args.reboot,
                brightness=args.brightness,
            )
        )
    except Exception as exc:
        print(f"Error: {exc}")
