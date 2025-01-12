import asyncio
import http
import os
import socketserver
import threading

import websockets
from http.server import SimpleHTTPRequestHandler
from socketserver import TCPServer

import ScraperScripts

HOST = "192.168.1.7"

#cd online
#python -m http.server 5554
#http://192.168.1.7:5554
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
    max_answers=3
    answers=[]
    tourney_ready=None
    async def parse_socket(self, websocket):
        async for message in websocket:
            addr = websocket.remote_address[0]
            if message:
                print(message)
                if message=='reconnected':
                    print('Reconnected')
                    self.godot_server = websocket
                elif not self.godot_server and HOST == addr:
                    self.godot_server = websocket
                    print(f'Connected to Godot')
                elif self.godot_server and HOST == addr:
                    if message=='ready':
                        self.tourney_ready=True
                        print('Tourney Ready')
                        for player in self.players:
                            await player.websocket.send(f'Lets Play')
                    elif len(message.split(':'))==2:
                        name,pick=message.split(':')
                        player = self.find_player_by_name(name)
                        print('ssomeone drafted')
                        # player.add_answers(pick)
                        self.answers.append(pick)
                        await player.websocket.send(f'{player.player_name}, drafted {pick}.')

                elif self.godot_server and addr not in self.players.keys() and HOST != addr:
                    await self.godot_server.send(f'player:{message}')
                    self.add_player(message, websocket)
                    print(f'{message} added')
                    await websocket.send(f"Got it, you're {message}.")
                elif self.godot_server and addr in self.players.keys() and HOST != addr and self.tourney_ready:
                    player = self.players[addr]
                    similar=ScraperScripts.word_match(message,self.answers,cutoff=0.8)
                    if not similar:
                        print('sent message to godot')
                        await self.godot_server.send(f'{player.player_name}:{message}')
                    else:
                        print('too similar')
                        await websocket.send(f'Too much like {similar}')
                    if player.websocket!=websocket:
                        player.websocket=websocket
                else:
                    print('something might be wrong')
                    await websocket.send(f"Not right now")

    def add_player(self, player_name, websocket):
        self.players[websocket.remote_address[0]] = Player(player_name,websocket)

    def find_player_by_name(self,player_name):
        reversed_dict = {value.player_name: key for key, value in self.players.items()}
        addr = reversed_dict.get(player_name)
        return self.players[addr]

handler = PlayerHandler()
PORT=5554
def start_http_server():
    with TCPServer((HOST, PORT), SimpleHTTPRequestHandler) as httpd:
        os.chdir("online")
        print(f"Serving HTTP on {HOST}:{PORT}")
        httpd.serve_forever()
        print('Its Over')

# Main entry point
async def main():
    # Start HTTP server in a separate thread
    # http_thread = threading.Thread(target=start_http_server, daemon=True)
    # http_thread.start()
# async def main():
    print('Server up')
    async with websockets.serve(handler.parse_socket, HOST, 5555,ping_interval=None):
        await asyncio.get_running_loop().create_future()  # run forever
    print('Its Over')
    # # Start the server
    # async :
    #     print(f"Serving HTTP on {HOST}:{PORT}")
    #     await httpd.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())


