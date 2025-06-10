import argparse
from womgr import (
    setup_device,
    WakeOnLanSwitch,
    PingBinarySensor,
    SystemCommandSwitch,
)


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

    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("wol", help="Send Wake-on-LAN packet")
    subparsers.add_parser("ping", help="Ping the device")
    subparsers.add_parser("restart", help="Restart the device")
    subparsers.add_parser("shutdown", help="Shut down the device")

    args = parser.parse_args()

    entry = setup_device(
        device_name=args.device_name,
        mac=args.mac,
        ip=args.ip,
        location=args.location,
        os_type=args.os_type,
        username=args.username,
        password=args.password,
    )

    wol = next(e for e in entry.entities if isinstance(e, WakeOnLanSwitch))
    ping = next(e for e in entry.entities if isinstance(e, PingBinarySensor))
    system = next(e for e in entry.entities if isinstance(e, SystemCommandSwitch))

    if args.command == "wol":
        wol.turn_on()
    elif args.command == "ping":
        success = ping.update()
        print("Device is reachable" if success else "Device is not reachable")
    elif args.command == "restart":
        system.restart()
    elif args.command == "shutdown":
        system.shutdown()


if __name__ == "__main__":
    main()
