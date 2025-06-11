import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
import requests

import womgr_cli
import dashboard_cli


def test_womgr_cli_invalid_mac(capsys):
    args = [
        "womgr_cli",
        "pc",
        "invalid",
        "1.2.3.4",
        "lab",
        "linux",
        "wol",
    ]
    with patch.object(sys, "argv", args), patch("womgr_cli.setup_device") as setup:
        womgr_cli.main()
        setup.assert_not_called()
    out = capsys.readouterr().out
    assert "Invalid MAC address" in out


def test_womgr_cli_parsing_calls_correct_command():
    class DummyWOL:
        def __init__(self):
            self.called = False

        def turn_on(self):
            self.called = True

    class DummyPing:
        def __init__(self):
            self.called = False

        def update(self):
            self.called = True

    class DummySystem:
        def restart(self):
            pass

        def shutdown(self):
            pass

    entry = SimpleNamespace(entities=[DummyWOL(), DummyPing(), DummySystem()])

    args = [
        "womgr_cli",
        "pc",
        "AA:BB:CC:DD:EE:FF",
        "1.2.3.4",
        "lab",
        "linux",
        "ping",
    ]
    with patch.object(sys, "argv", args), \
         patch("womgr_cli.setup_device", return_value=entry), \
         patch("womgr_cli.WakeOnLanSwitch", DummyWOL), \
         patch("womgr_cli.PingBinarySensor", DummyPing), \
         patch("womgr_cli.SystemCommandSwitch", DummySystem):
        womgr_cli.main()

    assert entry.entities[1].called
    

def test_dashboard_cli_main_parsing():
    args = ["dashboard_cli", "http://hass", "token", "pc"]
    with patch.object(sys, "argv", args), patch(
        "dashboard_cli.create_dashboard"
    ) as create:
        dashboard_cli.main()
        create.assert_called_once_with("http://hass", "token", "pc")


@patch("dashboard_cli.requests.get")
@patch("dashboard_cli.requests.post")
def test_create_dashboard_http_error(mock_post, mock_get):
    resp = MagicMock()
    resp.raise_for_status.side_effect = requests.HTTPError
    mock_get.return_value = resp
    with pytest.raises(requests.HTTPError):
        dashboard_cli.create_dashboard("http://hass", "token", "pc")
