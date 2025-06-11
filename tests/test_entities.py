import socket
import subprocess
from unittest.mock import patch

from womgr.entities import (
    WakeOnLanSwitch,
    PingBinarySensor,
    SystemCommandSwitch,
)


@patch("womgr.entities.socket.socket")
def test_wake_on_lan_turn_on(mock_socket):
    sock = mock_socket.return_value.__enter__.return_value
    switch = WakeOnLanSwitch("pc", "AA:BB:CC:DD:EE:FF")
    switch.turn_on()
    packet = b"\xff" * 6 + bytes.fromhex("aabbccddeeff") * 16
    mock_socket.assert_called_once_with(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt.assert_called_once_with(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto.assert_called_once_with(packet, ("<broadcast>", 9))


@patch("womgr.entities.subprocess.run")
def test_ping_update_linux(mock_run):
    mock_run.return_value.returncode = 0
    sensor = PingBinarySensor("pc", "1.2.3.4")
    with patch("womgr.entities.sys.platform", "linux"):
        assert sensor.update() is True
    mock_run.assert_called_once_with(
        ["ping", "-c", "1", "-W", "1", "1.2.3.4"], stdout=subprocess.DEVNULL
    )


@patch("womgr.entities.subprocess.run")
def test_ping_update_windows(mock_run):
    mock_run.return_value.returncode = 1
    sensor = PingBinarySensor("pc", "1.2.3.4")
    with patch("womgr.entities.sys.platform", "win32"):
        assert sensor.update() is False
    mock_run.assert_called_once_with(
        ["ping", "-n", "1", "-w", "1000", "1.2.3.4"], stdout=subprocess.DEVNULL
    )


@patch("womgr.entities.subprocess.Popen")
@patch("womgr.entities.shutil.which")
def test_system_command_restart_linux(mock_which, mock_popen):
    mock_which.side_effect = lambda cmd: f"/usr/bin/{cmd}"
    switch = SystemCommandSwitch("pc", "linux")
    switch.restart()
    mock_which.assert_called_once_with("reboot")
    mock_popen.assert_called_once_with(["sudo", "/usr/bin/reboot"])


@patch("womgr.entities.subprocess.Popen")
@patch("womgr.entities.shutil.which")
def test_system_command_restart_windows(mock_which, mock_popen):
    mock_which.return_value = None
    switch = SystemCommandSwitch("pc", "windows")
    switch.restart()
    mock_which.assert_called_once_with("shutdown")
    mock_popen.assert_called_once_with(["shutdown", "/r", "/t", "0"])


@patch("womgr.entities.subprocess.Popen")
@patch("womgr.entities.shutil.which")
def test_system_command_shutdown_linux(mock_which, mock_popen):
    mock_which.side_effect = lambda cmd: f"/sbin/{cmd}"
    switch = SystemCommandSwitch("pc", "linux")
    switch.shutdown()
    mock_which.assert_called_once_with("shutdown")
    mock_popen.assert_called_once_with(["sudo", "/sbin/shutdown", "-h", "now"])


@patch("womgr.entities.subprocess.Popen")
@patch("womgr.entities.shutil.which")
def test_system_command_shutdown_windows(mock_which, mock_popen):
    mock_which.return_value = "C:/shutdown.exe"
    switch = SystemCommandSwitch("pc", "windows")
    switch.shutdown()
    mock_which.assert_called_once_with("shutdown")
    mock_popen.assert_called_once_with(["C:/shutdown.exe", "/s", "/t", "0"])
