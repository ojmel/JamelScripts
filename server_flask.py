import multiprocessing
import os
import re
import subprocess
import sys
import flask
import requests
from flask import Flask, render_template, request
from flask_socketio import SocketIO, Namespace, emit
import ScraperScripts
import pathlib
from engineio.async_drivers import gevent
#pyinstaller -F --add-binary="draft_godot.exe;." --add-data="templates;templates" --hidden-import=ScraperScripts --hidden-import=engineio.async_threading -p .  .\server_flask.py& C:/Users/jamel/PycharmProjects/JamelScripts/.venv/Scripts/python.exe c:/Users/jamel/PycharmProjects/JamelScripts/server_flask.py

class PlayerInfo:
    name = None
    addr = None
    sid = None

    def __init__(self, name, addr, sid):
        self.name = name
        self.addr = addr
        self.sid = sid


class PlayerHandler:
    players: dict[str, PlayerInfo] = {}  # addr:PlayerInfo
    host_player = None
    godot_server = None
    answers = []
    game_state = 'wait'
    tourney_ready = None
    draft_done = None
    topic=''

    def check_for_player_name(self, name):
        return name in [player.name for player in self.players.values()]

    def check_for_player_addr(self, addr):
        return addr in [player.addr for player in self.players.values()]

    def add_player(self, name, addr, sid):
        self.players[addr] = PlayerInfo(name, addr, sid)
        print(f'{name} added')

    def find_player_by_name(self, player_name):
        reversed_dict = {value.name: key for key, value in self.players.items()}
        print(reversed_dict)
        addr = reversed_dict.get(player_name)
        print(addr)
        return self.players[addr]


app = Flask(__name__)
socketio = SocketIO(app,ping_timeout=30,async_mode='gevent')
HOST = "192.168.1.12"
HTTP_PORT = 5554

#python server_flask.py

@app.route("/")
def index():
    return render_template('Draft.html', addr=f'ws://{HOST}:{HTTP_PORT}')

# TODO I might be able to use this to make a whole different app for the host
@app.route('/shutdown')
def shutdown():
    socketio.stop()
    return "Server shutting down..."


class GodotServer(Namespace):
    def on_connect(self):
        print(f"godot connected")
        handler.godot_server = request.sid
        emit('connected', True)

    def on_ready(self, message):
        print(message)
        if message == 'vote':
            handler.draft_done = True
            handler.game_state = message
            print('Vote Ready')
        else:
            handler.tourney_ready = True
            print('Tourney Ready')
            handler.game_state = 'draft'
            handler.topic=message
        emit('game_state', {'state': handler.game_state, 'in_game': True,'topic':handler.topic}, broadcast=True,namespace='/player')

    def on_notify_player(self, message):
        print(message)
        if message['action'] == 'confirm_pick':
            print('someone drafted')
            handler.answers.append(message['pick'])
        emit('notify_player', message, namespace='/player', to=handler.find_player_by_name(message['name']).sid)

    def on_disconnect(self):
        print(f"godot disconnected")


class Player(Namespace):
    def on_connect(self, _data):
        player = handler.players.get(request.remote_addr)
        if handler.check_for_player_addr(request.remote_addr) and player:
            if player.sid != request.sid:
                player.sid = request.sid
        print(f"Client connected to {request.sid} namespace.")
        emit('game_state', {'state': handler.game_state, 'in_game': handler.check_for_player_addr(request.remote_addr),'topic':handler.topic},
             to=request.sid)

    def on_new_player(self, message):
        if handler.godot_server and not handler.check_for_player_addr(request.remote_addr):
            if not handler.check_for_player_name(message['name']):
                emit('new_player', message, to=handler.godot_server, namespace='/godot')
                handler.add_player(message['name'], request.remote_addr, request.sid)
                message['action']='confirm_player'
                emit('notify_player', message)
            else:
                emit('too_similar', 'Too much like another player')

    def on_draft_pick(self, message):
        print(message)
        if handler.tourney_ready:
            player = handler.players[request.remote_addr]
            similar = ScraperScripts.word_match(message['pick'], handler.answers, cutoff=0.8)
            if not similar:
                message['name'] = player.name
                emit('draft_pick', message, to=handler.godot_server, namespace='/godot')
            else:
                emit('too_similar', f'Too much like {similar}')

    def on_vote(self, message):
        if handler.draft_done:
            player = handler.players[request.remote_addr]
            message['name'] = player.name
            emit('vote', message, to=handler.godot_server, namespace='/godot')

    def on_host(self, message):
        print(message)
        if not handler.host_player:
            handler.host_player = request.remote_addr
            emit('notify_player', {'action': 'confirm_host'})

        elif handler.host_player == request.remote_addr:
            if message == 'make_host':
                emit('notify_player', {'action': 'confirm_host'})
            elif handler.godot_server:
                emit('host', message, to=handler.godot_server, namespace='/godot')

    def on_disconnect(self):
        print(f"Client disconnected from {self.namespace} namespace")


# Register the namespace
socketio.on_namespace(GodotServer('/godot'))
socketio.on_namespace(Player('/player'))


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


handler = PlayerHandler()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def run_godot(shutdown_address):
    godot=subprocess.Popen([resource_path('draft_godot.exe')])
    godot.wait()
    requests.get(shutdown_address)
    print('Shutting Down')

if __name__=='__main__':
    if ipv4 := get_ipv4():
        HOST = ipv4
    multiprocessing.freeze_support()
    process=multiprocessing.Process(target=run_godot,args=(f"http://{HOST}:{HTTP_PORT}/shutdown",))
    process.start()
    print(HOST)
    socketio.run(app, host=HOST, port=HTTP_PORT)
