import argparse
import asyncio
from womgr import (
    setup_device,
    WakeOnLanSwitch,
    PingBinarySensor,
    SystemCommandSwitch,
)
from womgr.util import parse_mac_address


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Simple CLI for HaWoManager device operations"
    )
    parser.add_argument("device_name", help="Name of the device")
    parser.add_argument("mac", help="MAC address of the device")
    parser.add_argument("ip", help="IP address of the device")
    parser.add_argument("location", help="Physical location of the device")
    parser.add_argument(
        "os_type", help="Operating system type (linux or windows)")
    parser.add_argument(
        "--username", default="", help="Username for restart/shutdown commands"
    )
    parser.add_argument(
        "--password", default="", help="Password for restart/shutdown commands"
    )
    parser.add_argument(
        "--color", default="", help="Bubble card background color"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("wol", help="Send Wake-on-LAN packet")
    subparsers.add_parser("ping", help="Ping the device")
    subparsers.add_parser("restart", help="Restart the device")
    subparsers.add_parser("shutdown", help="Shut down the device")
    subparsers.add_parser(
        "status", help="Check ping and system command availability"
    )

    args = parser.parse_args()

    try:
        parse_mac_address(args.mac)
    except ValueError:
        print("Invalid MAC address")
        return

    if args.os_type.lower() not in {"linux", "windows"}:
        print(f"Invalid OS type: {args.os_type}. Choose 'linux' or 'windows'.")
        return

    entry = setup_device(
        device_name=args.device_name,
        mac=args.mac,
        ip=args.ip,
        location=args.location,
        os_type=args.os_type,
        username=args.username,
        password=args.password,
        color=args.color,
    )

    wol = next(e for e in entry.entities if isinstance(e, WakeOnLanSwitch))
    ping = next(e for e in entry.entities if isinstance(e, PingBinarySensor))
    system = next(e for e in entry.entities if isinstance(e, SystemCommandSwitch))

    if args.command == "wol":
        try:
            wol.turn_on()
        except ValueError as exc:
            print(str(exc))
            return
    elif args.command == "ping":
        success = asyncio.run(ping.update())
        print("Device is reachable" if success else "Device is not reachable")
    elif args.command == "restart":
        try:
            system.restart()
        except (FileNotFoundError, ValueError) as exc:
            print(str(exc))
    elif args.command == "shutdown":
        try:
            system.shutdown()
        except (FileNotFoundError, ValueError) as exc:
            print(str(exc))
    elif args.command == "status":
        success = asyncio.run(ping.update())
        print("Device is reachable" if success else "Device is not reachable")
        try:
            availability = system.available_commands()
            print(
                f"Restart available: {availability['restart']}\nShutdown available: {availability['shutdown']}"
            )
        except ValueError as exc:
            print(str(exc))


if __name__ == "__main__":
    main()
