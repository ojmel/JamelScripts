import re
import subprocess

from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)
HOST = "192.168.1.12"
HTTP_PORT = 5554

@app.route("/")
def index():
    return render_template(r"Draft.html" , addr=f'ws://{HOST}:{HTTP_PORT}')


@socketio.on("message")
def handle_message(msg):
    print(f"Received message: {msg}")
    socketio.send(f"Server received: {msg}")  # Send response back

def get_ipv4():
    try:
        # Run ipconfig and capture the output
        result = subprocess.run(["ipconfig"], capture_output=True, text=True, check=True)
        output = result.stdout

        # Find all IPv4 addresses in the output
        ipv4 = re.findall(r"IPv4 Address[.\s]*:\s*([\d.]+)", output)[-1]
        return ipv4
    except Exception as e:
        return HOST

if __name__ == "__main__":
    if ipv4 := get_ipv4():
        HOST = ipv4
    print(HOST)
    socketio.run(app, debug=True, host=HOST,port=HTTP_PORT)
