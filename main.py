# echo-client.py
import random
import socket
import time


HOST = "gpn-tron.duckdns.org"  # The server's hostname or IP address
PORT = 4000  # The port used by the server
DIRS = [b"up", b"right", b"down", b"left"]

class GameBoard:
    def __init__(self, size):
        self.size = size
        self.board = [[0 for _ in range(self.size)] for _ in range(self.size)]
    def pos(self, move):
        self.board[int(move[2])][int(move[3])] = int(move[1])

    def remove(self, player):
        for row in self.board:
            for i in range(len(row)):
                if row[i] == player:
                    row[i] = 0

    def __str__(self):
        string = ''
        for row in self.board:
            for cell in row:
                if cell == 0:
                    string += '   |'
                else:
                    string += f"{cell:^3}|"
            string = string[:-1] + '\n'
        return string



def spl_v1(s):
    slashs = [i for i, ltr in enumerate(s) if ltr == 10]
    for slash in slashs:
        s = s[:slash] + b'|' + s[slash+1:]
    pipes = [i for i, ltr in enumerate(s) if ltr == 124]
    pipes.append(len(s))
    pipes.insert(0, -1)
    return [s[pipes[i]+1:pipes[i+1]].decode() for i in range(len(pipes)-1)]

def spl(s):
    string = s.decode()
    commands = string.split("\n")
    data = [c.split('|') for c in commands]
    return data


def main():
    direc = {"i": b'down', 'u': b'up', 'h': b'left', 'e': b'right'}

    old_data = ''
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        s.send(b'join|OF15-15|love<3\n')
        gb = None
        width, height, id, dir = 0, 0, 0, 0
        players = []
        while True:
            data = s.recv(1024)
            if data != old_data or random.random() > 0.9:
                old_data = data
                spl_data = spl(data)
                #i = input()
                #s.send(b'move|' + direc[i] + b'\n')
                for move in spl_data:
                    match move[0]:
                        case "":
                            pass
                        case "game":
                            gb = GameBoard(int(move[1]))
                            width, height, id = move[1:]
                            s.send(b'move|up\n')
                            print(f"game started ({width}x{height}) as player {id}")
                        case "tick":
                            print(gb)
                            dir = choose_dir()
                            s.send(b'move|' + DIRS[dir] + b'\n')
                        case "pos":
                            gb.pos(move)
                        case "player":
                            players.append([0, 0])
                        case "die":
                            for pl in move[1:]:
                                gb.remove(pl)
                        case _:
                            print(move)

    except Exception as e:
        raise(e)
    finally:
        s.shutdown(1)
        s.close()

def choose_dir():
    return 0#random.randint(0, 3)

main()
