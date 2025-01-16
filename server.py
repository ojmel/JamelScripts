import asyncio
import http
import os
import socketserver
import threading
import subprocess
import re
import websockets
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

import ScraperScripts

HOST = "192.168.1.12"


#cd online
#python -m http.server 5554
#http://192.168.1.12:5554
#Use qr code https://qr.io/ for web address
class Player:
    answers = []

    def __init__(self, player_name, websocket):
        self.websocket = websocket
        self.addr = websocket.remote_address[0]
        self.player_name = player_name

    def add_answers(self, message):
        self.answers.append(message)


class PlayerHandler:
    players: dict[str, Player] = {}
    godot_server = None
    max_answers = 3
    answers = []
    tourney_ready = None

    async def parse_socket(self, websocket):
        async for message in websocket:
            addr = websocket.remote_address[0]
            if message:
                print(message)
                if HOST == addr:
                    await self.manage_godot(message, websocket)
                elif HOST != addr:
                    await self.manage_player(message, websocket)
                else:
                    print('something might be wrong')
                    await websocket.send(f"Not right now")

    async def add_player(self, player_name, websocket):
        self.players[websocket.remote_address[0]] = Player(player_name, websocket)
        await self.godot_server.send(f'player:{player_name}')
        print(f'{player_name} added')
        await websocket.send(f"Got it, you're {player_name}.")

    async def manage_player(self, message, websocket):
        addr = websocket.remote_address[0]
        print(addr)
        if self.godot_server and addr not in self.players.keys():
            await self.add_player(message, websocket)
        elif addr in self.players.keys() and self.tourney_ready:
            player = self.players[addr]
            similar = ScraperScripts.word_match(message, self.answers, cutoff=0.8)
            if not similar:
                print('sent message to godot')
                await self.godot_server.send(f'{player.player_name}:{message}')
            else:
                print('too similar')
                await websocket.send(f'Too much like {similar}')
            if player.websocket != websocket:
                player.websocket = websocket

    async def manage_godot(self, message, websocket):
        if not self.godot_server:
            self.godot_server = websocket
            print(f'Connected to Godot')
        elif self.godot_server:
            if self.godot_server != websocket:
                self.godot_server = websocket

            if message == 'ready':
                self.tourney_ready = True
                print('Tourney Ready')
                # for player in self.players.values():
                #     await player.websocket.send(f'Lets Play')

            elif message.startswith('next'):
                _, player_name = message.split('%')
                player = self.find_player_by_name(player_name)
                await player.websocket.send("You're Up")
            elif len(message.split(':')) == 2:
                name, pick = message.split(':')
                player = self.find_player_by_name(name)
                print('someone drafted')
                self.answers.append(pick)
                await player.websocket.send(f'{player.player_name}, drafted {pick}.')

    def find_player_by_name(self, player_name):
        reversed_dict = {value.player_name: key for key, value in self.players.items()}
        addr = reversed_dict.get(player_name)
        return self.players[addr]


handler = PlayerHandler()
HTTP_PORT = 5554


class MyHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.path = "/Draft.html"
        return super().do_GET()


def start_http_server():
    with TCPServer((HOST, HTTP_PORT), MyHandler) as httpd:
        os.chdir("online")
        print(f"Serving HTTP on {HOST}:{HTTP_PORT}")
        httpd.serve_forever()
        print('Its Over')


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


async def main():
    http_thread = threading.Thread(target=start_http_server, daemon=True)
    http_thread.start()
    print(f'Server up {HOST}:5555')
    async with websockets.serve(handler.parse_socket, HOST, 5555, ping_interval=None):
        await asyncio.get_running_loop().create_future()  # run forever


if __name__ == "__main__":
    if ipv4 := get_ipv4():
        HOST = ipv4

    asyncio.run(main())
