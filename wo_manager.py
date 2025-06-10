import os
import json
import subprocess
from flask import Flask, render_template, redirect, url_for, request
from wakeonlan import send_magic_packet

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(BASE_DIR, 'templates', 'womanager.html')
CONFIG_FILE = os.path.join(BASE_DIR, 'devices.json')

app = Flask(__name__)


def ensure_dashboard():
    os.makedirs(os.path.join(BASE_DIR, 'templates'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'static'), exist_ok=True)
    if not os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, 'w') as f:
            f.write("""<!doctype html>
<html lang='en'>
  <head>
    <meta charset='utf-8'>
    <title>WoManager</title>
    <link rel='stylesheet' href='/static/styles.css'>
  </head>
  <body>
    <h1>WoManager Dashboard</h1>
    <div class='grid'>
      {% for d in devices %}
      <div class='card'>
        <h2>{{ d.name }}</h2>
        <p>Status: {% if d.status %}Online{% else %}Offline{% endif %}</p>
        <div class='actions'>
          <form method='post' action='/wol/{{ d.mac }}'><button type='submit'>Wake</button></form>
          <form method='post' action='/restart/{{ d.ip }}'><button type='submit'>Restart</button></form>
          <form method='post' action='/shutdown/{{ d.ip }}'><button type='submit'>Shutdown</button></form>
        </div>
      </div>
      {% endfor %}
    </div>
  </body>
</html>""")
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"devices": []}, f)


def load_devices():
    if not os.path.exists(CONFIG_FILE):
        return []
    with open(CONFIG_FILE) as f:
        data = json.load(f)
    devices = data.get('devices', [])
    for d in devices:
        d['status'] = check_status(d.get('ip'))
    return devices


def check_status(ip: str) -> bool:
    if not ip:
        return False
    try:
        result = subprocess.run(['ping', '-c', '1', '-W', '1', ip], stdout=subprocess.DEVNULL)
        return result.returncode == 0
    except Exception:
        return False


def remote_cmd(ip: str, command: str):
    try:
        subprocess.run(['ssh', ip, command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
    except Exception as exc:
        print(f"Failed to run {command} on {ip}: {exc}")


def restart_device(ip: str):
    remote_cmd(ip, 'sudo reboot')


def shutdown_device(ip: str):
    remote_cmd(ip, 'sudo shutdown now')


@app.route('/')
def index():
    return redirect(url_for('dashboard'))


@app.route('/WoManager')
def dashboard():
    devices = load_devices()
    return render_template('womanager.html', devices=devices)


@app.route('/wol/<mac>', methods=['POST'])
def wake(mac):
    send_magic_packet(mac)
    return redirect(url_for('dashboard'))


@app.route('/restart/<ip>', methods=['POST'])
def restart(ip):
    restart_device(ip)
    return redirect(url_for('dashboard'))


@app.route('/shutdown/<ip>', methods=['POST'])
def shutdown(ip):
    shutdown_device(ip)
    return redirect(url_for('dashboard'))


if __name__ == '__main__':
    ensure_dashboard()
    app.run(host='0.0.0.0', port=5000)
