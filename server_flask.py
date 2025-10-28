import multiprocessing
import os
import re
import subprocess
import sys
from enum import Enum
import requests
from flask import Flask, render_template, request
from flask_socketio import SocketIO, Namespace, emit
import ScraperScripts
import pathlib
from engineio.async_drivers import gevent
#pyinstaller -F --add-binary="draft_godot.exe;." --add-data="templates;templates" --hidden-import=ScraperScripts --hidden-import=engineio.async_threading -p .  .\server_flask.py

class PlayerInfo:
    name = None
    addr = None
    sid = None

    def __init__(self, name, addr, sid):
        self.name = name
        self.addr = addr
        self.sid = sid


class GameState(Enum):
    signup = 'wait'
    drafting = 'draft'
    voting = 'vote'

class PlayerHandler:
    restarting_players={}
    players: dict[str, PlayerInfo] = {}  # addr:PlayerInfo
    host_player = None
    godot_server = None
    answers = []
    game_state: GameState = GameState.signup
    tourney_ready = False
    draft_done = False
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
HOST = ""
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
    def on_matchup(self,message):
        emit('matchup', message, broadcast=True,
             namespace='/player')
    def on_ready(self, message):
        print(message)
        if message == 'vote':
            handler.draft_done = True
            handler.game_state = GameState.voting
            print('Vote Ready')
        else:
            handler.tourney_ready = True
            print('Tourney Ready')
            handler.game_state = GameState.drafting
            handler.topic=message
        emit('game_state', {'state': handler.game_state.value, 'in_game': True,'topic':handler.topic}, broadcast=True,namespace='/player')

    def on_notify_player(self, message):
        print(message)
        match message['action']:
            case 'confirm_pick':
                print('someone drafted')
                handler.answers.append(message['pick'])

            case 'topic':
                if handler.host_player:
                    emit('notify_player', {'action': 'topic'}, namespace='/player',
                         to=handler.players[handler.host_player].sid)
                else:
                    emit('topic_select', {'topic':'Topic'})
                return
            case 'sudden_death':
                for player,picks in message['info'].items():
                    emit('notify_player', {'action': 'sudden_death', 'info': picks} , namespace='/player', to=handler.find_player_by_name(player).sid)
                return
            case 'vote':
                print({'action':'snitch','names':message['names']})
                emit('notify_player', {'action':'snitch','names':message['names']}, namespace='/player', to=handler.players[handler.host_player].sid)
                for player in message['names']:
                    emit('notify_player', message, namespace='/player', to=handler.find_player_by_name(player).sid)
                return

        emit('notify_player', message, namespace='/player', to=handler.find_player_by_name(message['name']).sid)

    def on_restart(self, message):
        print('123456')
        emit('notify_player', {'action':'restart'},broadcast=True,namespace='/player')
        handler.restarting_players=dict(handler.players)
        handler.players = {}  # addr:PlayerInfo
        handler.answers = []
        handler.game_state = GameState.signup
        handler.tourney_ready = False
        handler.draft_done = False
        handler.host_player = None
        handler.topic = ''
        emit('game_state', {'state': handler.game_state.value, 'in_game': False, 'topic': handler.topic}, broadcast=True,
             namespace='/player')

    def on_disconnect(self):
        print(f"godot disconnected")


class Player(Namespace):
    def on_connect(self, _data):
        print(request.remote_addr)
        player = handler.players.get(request.remote_addr)
        if handler.check_for_player_addr(request.remote_addr) and player:
            if player.sid != request.sid:
                player.sid = request.sid
        print(f"Client connected to {request.sid} namespace.")
        emit('game_state', {'state': handler.game_state.value, 'in_game': handler.check_for_player_addr(request.remote_addr),'topic':handler.topic},
             to=request.sid)

    def on_new_player(self, message):
        #message: { name: inputField.value }
        print(message)
        if handler.godot_server and not handler.check_for_player_addr(request.remote_addr) and GameState.signup:
            if not handler.check_for_player_name(message['name']):
                emit('new_player', message, to=handler.godot_server, namespace='/godot')
                handler.add_player(message['name'], request.remote_addr, request.sid)
                message['action']='confirm_player'
                emit('notify_player', message)
                emit('game_state',
                     {'state': handler.game_state.value, 'in_game': handler.check_for_player_addr(request.remote_addr),
                      'topic': handler.topic})
            else:
                emit('too_similar', 'Too much like another player')

    def on_draft_pick(self, message):
        print(message)
        if handler.tourney_ready:
            player = handler.players[request.remote_addr]
            similar = ScraperScripts.word_match(message['pick'], handler.answers, cutoff=0.45)
            if not similar:
                message['name'] = player.name
                emit('draft_pick', message, to=handler.godot_server, namespace='/godot')
            else:
                emit('too_similar', {'warning':f'Someone already drafted {similar}','pick':message['pick']})

    def on_draft_override(self,message):
        if handler.tourney_ready:
            player = handler.players[request.remote_addr]
            message['name'] = player.name
            emit('draft_pick', message, to=handler.godot_server, namespace='/godot')

    def on_sudden_death(self,message):
        player = handler.players[request.remote_addr]
        message['name'] = player.name
        emit('sudden_death', message, to=handler.godot_server, namespace='/godot')

    def on_vote(self, message):
        if handler.draft_done:
            player = handler.players[request.remote_addr]
            message['name'] = player.name
            emit('vote', message, to=handler.godot_server, namespace='/godot')

    def on_host(self, message):
        print(message)
        if not handler.host_player:
            handler.host_player = request.remote_addr
            print(handler.host_player)
            emit('notify_player', {'action': 'confirm_host'})

        elif handler.host_player == request.remote_addr:
            if message == 'make_host':
                emit('notify_player', {'action': 'confirm_host'})
            elif isinstance(message,dict) and handler.godot_server:
                emit('topic_select', message, to=handler.godot_server, namespace='/godot')
            elif handler.godot_server:
                emit('host', message, to=handler.godot_server, namespace='/godot')

    def on_restart(self, message:bool):
        #message: bool
        player = handler.restarting_players[request.remote_addr].name
        if message and GameState.signup:
            if not handler.check_for_player_name(player):
                message={'name':player}
                emit('new_player', message, to=handler.godot_server, namespace='/godot')
                handler.add_player(player, request.remote_addr, request.sid)
                message['action']='confirm_player'
                emit('notify_player', message)
                emit('game_state',
                     {'state': handler.game_state.value, 'in_game': handler.check_for_player_addr(request.remote_addr),
                      'topic': handler.topic})
            else:
                emit('too_similar', 'Too much like another player')

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
        output=output.split('Wireless LAN adapter Wi-Fi')[-1]
        # Find all IPv4 addresses in the output
        ipv4 = re.findall(r"IPv4 Address[.\s]*:\s*([\d.]+)", output)[0]
        return ipv4
    except Exception as e:
        return HOST


handler = PlayerHandler()

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def run_godot(shutdown_address):
    godot=subprocess.Popen([resource_path('draft_godot_v6.exe')])
    godot.wait()
    requests.get(shutdown_address)
    print('Shutting Down')

if __name__=='__main__':
    if ipv4 := get_ipv4():
        HOST = ipv4
    # multiprocessing.freeze_support()
    # process=multiprocessing.Process(target=run_godot,args=(f"http://{HOST}:{HTTP_PORT}/shutdown",))
    # process.start()
    print(HOST,HTTP_PORT)
    socketio.run(app, host=HOST, port=HTTP_PORT)
