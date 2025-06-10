# HaWoManager Control API

This repository provides a minimal REST API for sending Wake-on-LAN magic packets as well as triggering system restart or shutdown.

## Usage

Install dependencies and run the server:

```bash
pip install -r requirements.txt
python control_api.py
```

### Configuration

- `API_TOKEN`: optional. If set, requests must include this value in the `X-API-Token` header or `token` query parameter.
- `ENABLE_CONTROL_API`: defaults to `false`. When set to `true`, the `/api/restart` and `/api/shutdown` endpoints will execute `shutdown` commands on the host.

### Endpoints

| Endpoint | Method | Description |
| --- | --- | --- |
| `/api/wol` | POST | Body contains `{ "mac": "aa:bb:cc:dd:ee:ff" }`. Sends a WOL packet. |
| `/api/restart` | POST | Restarts the host if enabled. |
| `/api/shutdown` | POST | Shuts down the host if enabled. |

## Security considerations

- Exposing restart and shutdown controls may allow remote users to disrupt the system. Require a strong `API_TOKEN` and limit network access (e.g. firewall).
- Keep the server on a trusted network segment; HTTPS termination or a reverse proxy is recommended.
- Disable the endpoints by omitting `ENABLE_CONTROL_API` or setting it to any value other than `true`.

