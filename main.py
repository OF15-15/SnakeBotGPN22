import random
import socket
import time
import numpy as np

# host and port to connect to the server
HOST = "gpn-tron.duckdns.org"
PORT = 4000
# the four possible directions
DIRS = [b"up", b"right", b"down", b"left"]

class Game:
    def __init__(self, id, size):
        self.players = [Player(i) for i in range(size//2)]
        self.me = self.players[id]
        self.size = size
        self.board = np.full((size, size), -1)

    def update_head_pos(self, pos, player_id):
        self.board[pos[0]][pos[1]] = player_id
        self.players[player_id].head = pos

    def remove(self, player_id):
        """Removes a player that died"""
        for j in range(self.size):
            for i in range(self.size):
                if self.board[j][i] == player_id:
                    self.board[j][i] = -1
        self.players[player_id].alive = False
        print("removed player", player_id)

    def free(self, pos, dirs, konjunk=True):
        """Returns if the square in the specified directions are empty"""
        dirs = [d % 4 for d in dirs]
        bools = []
        if 0 in dirs: bools.append(self.board[(pos[0] - 1) % self.size][pos[1] % self.size] == -1)
        if 1 in dirs: bools.append(self.board[pos[0] % self.size][(pos[1] + 1) % self.size] == -1)
        if 2 in dirs: bools.append(self.board[(pos[0] + 1) % self.size][pos[1] % self.size] == -1)
        if 3 in dirs: bools.append(self.board[pos[0] % self.size][(pos[1] - 1) % self.size] == -1)
        if konjunk: return all(bools)
        return any(bools)

    def __str__(self):
        string = ''
        for row in self.board:
            for cell in row:
                if cell == -1:
                    string += '   |'
                else:
                    string += f"{cell:^3}|"
            string = string[:-1] + '\n'
        return string




class Player:
    def __init__(self, id):
        self.id = id
        self.head_pos = [0, 0]
        self.alive = True


def spl(s):
    """split the incoming binary string into a 2d list"""
    string = s.decode()
    commands = string.split("\n")
    data = [[int(elem) if elem.isdigit() else elem for elem in c.split('|')] for c in commands]
    return data

def move(pos, direction):
    """move a position in a given direction"""
    if direction == 0:
        return [pos[0] - 1, pos[1]]
    elif direction == 1:
        return [pos[0], pos[1] + 1]
    elif direction == 2:
        return [pos[0] + 1, pos[1]]
    elif direction == 3:
        return [pos[0], pos[1] - 1]
    return pos

def main():
    """main game loop"""
    # catch all errors to prevent quitting tcp without closing
    try:
        # socket setup & join command
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((HOST, PORT))
        with open("pw.txt") as f:
            string = f.read().split('\n')

        s.send(b'join|' + string[0].encode() + b'|' + string[1].encode() + b'\n')

        # declare vars
        old_data = ''
        game = None

        # loop
        while True:
            # wait for data
            raw_data = s.recv(1024)
            # if nothing changed, don't do anything
            if raw_data != old_data:
                old_data = raw_data
                spl_data = spl(raw_data)

                for move in spl_data:
                    # iterate over all moves and perform a case matching the command
                    match move[0]:
                        case "":
                            pass
                        case "game":
                            # starting a new game: reset the board, start with moving upwards
                            game = Game(move[3], move[2])
                            # width, height, id = move[1:]
                            s.send(b'chat|running the nets\n')
                            s.send(b'move|up\n')
                            print(f"game started ({game.size}x{game.size}) as player {game.me.id}")
                        case "tick":
                            # one gamestep
                            # print current board
                            print(game)
                            # call choose_dir() func to set a new direction and move there
                            dir = choose_dir(game)
                            print(DIRS[dir])
                            s.send(b'move|' + DIRS[dir] + b'\n')
                        case "pos":
                            print(move)
                            # update a player's position
                            game.update_head_pos(np.array([move[3], move[2]]), move[1])
                        case "player":
                            # initialize a new player, seems unnecessary currently
                            pass
                        case "die":
                            # remove a dead player from the game board
                            for pl in move[1:]:
                                game.remove(pl)

                        case _:
                            # if unknown, just print it
                            print(move)

    except Exception as e:
        # raise the catched exeptions again
        raise (e)
    finally:
        # make sure to shutdown and close the tcp connection correctly
        s.shutdown(1)
        s.close()

def choose_dir(game):
    """choose the next direction for the player"""
    return 0

# start the main loop
main()
