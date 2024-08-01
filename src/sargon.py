#!/usr/bin/env python

import re
import time
import socket
import subprocess
import vice_monitor
from enum import Enum
from vice_connect import vice_read_mem

sargon_prg = "vic20-sargon-ii-chess/PRG/SargonII-2000.prg"

MON_PORT = 6510
MON_HOST = "127.0.0.1"

# Unprintable character codes for keyboard buffer using c-style hex escapes per vice manual
CHR_F1 = '\\x85'
CHR_RETURN = '\\x0d'
CHR_CURSOR_RIGHT = '\\x1d'
CHR_CURSOR_DOWN = '\\x11'


SCREEN_START = 0x1e00
SCREEN_WIDTH = 22
PIECE_WIDTH_CHARS = 2
PIECE_HEIGHT_CHARS = 2

ADDR_MOVE_NUM = 0x18


class Piece(Enum):
    ROOK = 0
    KNIGHT = 1
    BISHOP = 2
    QUEEN = 3
    KING = 4
    PAWN = 5


class Graphic(Enum):
    SOLID = 0
    OUTLINE = 1


class Colour(Enum):
    BLACK = 0
    WHITE = 1


class Square():

    def __init__(self, piece, graphic, colour):
        super().__init__()
        self.piece = piece
        self.graphic = graphic
        self.colour = colour

    def __repr__(self) -> str:
        if (self.piece is None):
            return f"empty {self.colour.name}"
        else:
            return f"{self.colour.name} {self.piece.name} {self.graphic.name}"


# reading the board state

# the board is always oriented the same way
# with white at the bottom, so the top left
# square is black, meaning the black piece
# there will use the outline graphic.

# petscii/ascii mapping in order:
# top-left, top-right, bottom-left, bottom-right
# top left char is unique therefore sufficient to
# read board position
PIECES = {
    'efgh': (Piece.ROOK, Graphic.SOLID),
    '_!"#': (Piece.ROOK, Graphic.OUTLINE),
    'ijkl': (Piece.KNIGHT, Graphic.SOLID),
    "$%&'": (Piece.KNIGHT, Graphic.OUTLINE),
    'mnop': (Piece.BISHOP, Graphic.SOLID),
    '()*+': (Piece.BISHOP, Graphic.OUTLINE),
    'qrst': (Piece.QUEEN, Graphic.SOLID),
    ',-./': (Piece.QUEEN, Graphic.OUTLINE),
    'uvst': (Piece.KING, Graphic.SOLID),
    '01./': (Piece.KING, Graphic.OUTLINE),
    '[\\]^': (Piece.PAWN, Graphic.OUTLINE),
    'abcd': (Piece.PAWN, Graphic.SOLID),
    '@@@@': None
}

# screen code for the custom character at the
# top left of the chess piece 2x2 char graphic
# which is sufficient to identify the piece at
# a board location because the top left char is
# unique while some other parts are shared
# e.g. Q,K bottoms
# high bit is 1 for white, 0 for black
# (reverse video version)
TOP_LEFT_SCREEN_CODE = {
    0x05: Square(Piece.ROOK, Graphic.SOLID, Colour.BLACK),
    0x24: Square(Piece.KNIGHT, Graphic.OUTLINE, Colour.BLACK),
    0x0d: Square(Piece.BISHOP, Graphic.SOLID, Colour.BLACK),
    0x2c: Square(Piece.QUEEN, Graphic.OUTLINE, Colour.BLACK),
    0x15: Square(Piece.KING, Graphic.SOLID, Colour.BLACK),
    0x28: Square(Piece.BISHOP, Graphic.OUTLINE, Colour.BLACK),
    0x09: Square(Piece.KNIGHT, Graphic.SOLID, Colour.BLACK),
    0x1f: Square(Piece.ROOK, Graphic.OUTLINE, Colour.BLACK),
    0x1b: Square(Piece.PAWN, Graphic.OUTLINE, Colour.BLACK),
    0x01: Square(Piece.PAWN, Graphic.SOLID, Colour.BLACK),
    0x80: Square(None, None, Colour.BLACK),
    0x00: Square(None, None, Colour.WHITE),
    0x9b: Square(Piece.PAWN, Graphic.OUTLINE, Colour.WHITE),
    0x81: Square(Piece.PAWN, Graphic.SOLID, Colour.WHITE),
    0x85: Square(Piece.ROOK, Graphic.SOLID, Colour.WHITE),
    0xa4: Square(Piece.KNIGHT, Graphic.OUTLINE, Colour.WHITE),
    0x8d: Square(Piece.BISHOP, Graphic.SOLID, Colour.WHITE),
    0xac: Square(Piece.QUEEN, Graphic.OUTLINE, Colour.WHITE),
    0x95: Square(Piece.KING, Graphic.SOLID, Colour.WHITE),
    0xa8: Square(Piece.BISHOP, Graphic.OUTLINE, Colour.WHITE),
    0x89: Square(Piece.KNIGHT, Graphic.SOLID, Colour.WHITE),
    0x9f: Square(Piece.ROOK, Graphic.OUTLINE, Colour.WHITE)
}

def build_tl_pieces(ps):
    """makes a pieces dict using just the top left char"""
    tl = {}
    for k, v in ps.items():
        tl[k[0]] = v
    return tl


def position_to_coord(position):
    """converts an algebraic position like a8 to top-left origin numeric grid tuple (0,0)"""
    return "abcdefgh".find(position.lower()[0]), 8 - int(position[1])

def ml_sc_pos(position):
    """returns the memory location of the top left of the screen grid for the position"""
    coord = position_to_coord(position)
    return sc_coord(coord)

def sc_coord(coord):
    """memory location of tl screen ch for for given board coord"""
    offset_file = coord[0] * PIECE_WIDTH_CHARS
    offset_rank = coord[1] * PIECE_HEIGHT_CHARS
    return offset_rank * SCREEN_WIDTH + offset_file + SCREEN_START

def screen_char(position):
    """gets the top left char for a given board position"""
    # calculate the memory location fo the top left char for
    # the position and get the screen char for that position
    return TOP_LEFT_SCREEN_CODE[ml_sc_pos(position)]

def piece_at(position):
    return TL_PIECES[screen_char(position)]

def coord_square_colour(coord):
    return Colour.WHITE if (coord[0] + coord[1]) % 2 == 0 else Colour.BLACK

def vmon(command):
    return vmon_basic(command)

def vmon_basic(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((MON_HOST, MON_PORT))
        # TODO ? does this block or do we need to specify a flag to make it block?
        s.sendall(command.encode('utf-8'))
        assert s.getblocking()
        data = s.recv(1024)
        return data.decode('utf-8')

def read_mem(start, finish):
    return vice_read_mem(host, port, start, finish)

def save_mem(filename):
    return vmon(f"s {filename} 0000 ffff")

def send_keys(keys):
    """
    Sets the keybuffer of the guest machine to the given string.
    Use c-style hex escapes for non-glyph keys
    """
    return vmon(f"keybuf {keys}\n")


def coord_to_pos(coord):
    return f"{"abcdefgh"[7-coord[0]]}{coord[1]+1}"

TL_PIECES = build_tl_pieces(PIECES)

def dump_board():
    for r in range(8):
        for f in range(8):
            coord = (f, r)
            addr = sc_coord(coord)
            data = vice_monitor.read_memory(addr, addr).data
            value = int(data[0])
            piece = TOP_LEFT_SCREEN_CODE[value]
            sq = coord_square_colour(coord)
            print(f"{coord_to_pos(coord)} {piece} on {sq.name}")
        print()

def dump_board_mem():
    for r in range(8):
        for f in range(8):
            coord = (f, r)
            addr = sc_coord(coord)
            data = vice_monitor.read_memory(addr, addr).data
            value = int(data[0])
            print(f"{coord} {coord_to_pos(coord)} @ {addr} {hex(addr)}) = {hex(value)} ", end="")
            piece = TOP_LEFT_SCREEN_CODE[value]
            print(piece)


def quit_vice():
    print(send_keys("quit"))


def sleep(t):
    print(f"sleeping {t}s")
    time.sleep(t)

def make_move(move):
    if re.fullmatch("^[a-hA-H][1-8]-[a-hA-H][1-8]$", move) is None:
        raise ValueError(f"move {move} not in src-dest form.")

    print(f"entering white move {move}")
    send_keys(f"{move.lower()}{CHR_RETURN}")
    sleep(2)


def start_game(colour, level):
    if level != int(level) or level < 0 or level > 6:
        raise ValueError(f"level {level} must an integer from 0-6.")
    print(f"starting game as {colour.name} on level {level}")
    send_keys(CHR_F1)
    send_keys(f"g{"w" if colour == Colour.WHITE else "b"}{level}")
    sleep(1)


def shift_screen(right, down):
    print("centering screen")
    send_keys(CHR_CURSOR_RIGHT * right + CHR_CURSOR_DOWN * down)


def start_sargon_vice():
    subprocess.Popen([
        "xvic", "-remotemonitor",
        "-remotemonitoraddress", f"ip4://{MON_HOST}:{MON_PORT}",
        "-binarymonitor",
        "-memory", "8k",
        "-autostartprgmode", "1",
        sargon_prg
    ], stdout=open('vice.out.log', 'w'), stderr=open('vice.err.log', 'w'))
    # TODO how do we clean up the process / kill etc?
    print("waiting for prg to load")
    sleep(6)


def read1(addr):
    return int(vice_monitor.read_memory(addr, addr).data[0])

def is_computer_move():
    # we could assume
    # human colour is 0x15, whos turn is 0x16 so grab both at once:
    data = vice_monitor.read_memory(0x15, 0x16).data
    return not data[0] == data[1]

def warp(is_warp):
    mode = "on" if is_warp else "off"
    send_keys(f"warp {mode}")

def await_computer():
    print("waiting for computer")
    time.sleep(0.5)
    while is_computer_move():
        print(".", end="")
        time.sleep(0.5)
    print()

def get_move_number():
    return read1(ADDR_MOVE_NUM)

def main():

    start_sargon_vice()
    shift_screen(7, 8)
    start_game(Colour.WHITE, 2)

    sleep(2)
    read_mem(0x15, 0x16)
    return

    # dump_board()
    make_move("d2-d4")

    await_computer()
    make_move("c1-f4")

    await_computer()

    make_move("e2-e3")
    await_computer()

    # quit_vice()


if __name__ == "__main__":
    main()
