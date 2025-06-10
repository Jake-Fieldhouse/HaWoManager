import os
import socket
import subprocess
from flask import Flask, request, jsonify

app = Flask(__name__)

API_TOKEN = os.environ.get('API_TOKEN')
ENABLE_CONTROL_API = os.environ.get('ENABLE_CONTROL_API', 'false').lower() == 'true'


def send_magic_packet(mac: str) -> None:
    clean_mac = mac.replace(':', '').replace('-', '')
    if len(clean_mac) != 12:
        raise ValueError('Incorrect MAC address format')
    data = bytes.fromhex('FF' * 6 + clean_mac * 16)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(data, ('<broadcast>', 9))


def require_token(func):
    def wrapper(*args, **kwargs):
        if API_TOKEN is None:
            return func(*args, **kwargs)
        token = request.headers.get('X-API-Token') or request.args.get('token')
        if token != API_TOKEN:
            return jsonify({'error': 'unauthorized'}), 401
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


@app.route('/api/wol', methods=['POST'])
@require_token
def wol():
    data = request.get_json(force=True)
    mac = data.get('mac')
    if not mac:
        return jsonify({'error': 'mac missing'}), 400
    try:
        send_magic_packet(mac)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    return jsonify({'status': 'packet sent'})


@app.route('/api/restart', methods=['POST'])
@require_token
def restart():
    if not ENABLE_CONTROL_API:
        return jsonify({'error': 'endpoint disabled'}), 403
    subprocess.Popen(['shutdown', '-r', 'now'])
    return jsonify({'status': 'restarting'})


@app.route('/api/shutdown', methods=['POST'])
@require_token
def shutdown():
    if not ENABLE_CONTROL_API:
        return jsonify({'error': 'endpoint disabled'}), 403
    subprocess.Popen(['shutdown', '-h', 'now'])
    return jsonify({'status': 'shutting down'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
