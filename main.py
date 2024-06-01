# echo-client.py
import random
import socket
import time
import numpy as np

# host and port to connect to the server
HOST = "gpn-tron.duckdns.org"
PORT = 4000
# the four possible directions
DIRS = [b"up", b"right", b"down", b"left"]

class GameBoard:
    """describes the current game state"""

    def __init__(self, size, id):
        self.size = size
        # saves all the data in a 2 dim array, -1 is empty
        # np to make it faster
        self.board = np.full((size, size), -1)
        self.id = id
        self.pos = [0, 0]

    def update_pos(self, move):
        """Update the Game when a player does a given move"""
        self.board[int(move[3])][int(move[2])] = int(move[1])
        # update your position if it's your move
        if int(move[1]) == self.id:
            self.pos = [int(move[3]), int(move[2])]

    def remove(self, player):
        """Removes a player that died"""
        for j in range(self.size):
            for i in range(self.size):
                if self.board[j][i] == player:
                    self.board[j][i] = -1
        print("removed player", player)

    def free(self, pos, dirs, konjunk = True):
        """Returns if the square in the specified directions are empty"""
        dirs = [d%4 for d in dirs]
        bools = []
        if 0 in dirs: bools.append(self.board[(pos[0] - 1) % self.size][pos[1] % self.size] == -1)
        if 1 in dirs: bools.append(self.board[pos[0] % self.size][(pos[1] + 1) % self.size] == -1)
        if 2 in dirs: bools.append(self.board[(pos[0] + 1) % self.size][pos[1] % self.size] == -1)
        if 3 in dirs: bools.append(self.board[pos[0] % self.size][(pos[1] -1 ) % self.size] == -1)
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

def spl(s):
    """split the incoming binary string into a 2d list"""
    string = s.decode()
    commands = string.split("\n")
    data = [c.split('|') for c in commands]
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
        gb = None
        players = []

        # loop
        while True:
            # wait for data
            raw_data = s.recv(1024)
            # if nothing changed, don't do anything
            if raw_data != old_data:
                old_data = raw_data
                spl_data = spl(raw_data)
                # direct user input
                # i = input()
                # s.send(b'move|' + direc[i] + b'\n')
                for move in spl_data:
                    # iterate over all moves and perform a case matching the command
                    match move[0]:
                        case "":
                            pass
                        case "game":
                            #test
                            # starting a new game: reset the board, start with moving upwards
                            gb = GameBoard(int(move[1]), int(move[3]))
                            # width, height, id = move[1:]
                            s.send(b'chat|running the nets\n')
                            s.send(b'move|up\n')
                            print(f"game started ({gb.size}x{gb.size}) as player {gb.id}")
                        case "tick":
                            # one gamestep
                            # print current board
                            print(gb)
                            # call choose_dir() func to set a new direction and move there
                            dir = choose_dir(gb)
                            print(DIRS[dir])
                            s.send(b'move|' + DIRS[dir] + b'\n')
                        case "pos":
                            # update a player's position
                            gb.update_pos(move)
                        case "player":
                            # initialize a new player, seems unnecessary currently
                            pass
                        case "die":
                            # remove a dead player from the game board
                            for pl in move[1:]:
                                gb.remove(int(pl))
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

def choose_dir(gb):
    """choose the next direction for the player"""
    print(gb.pos, gb.id)
    for i in range(4):
        if gb.free(gb.pos, [i]) and gb.free(move(gb.pos, i), [i-1, i, i+1], False):
            return i
    return 0

# start the main loop
main()
