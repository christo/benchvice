#!/usr/bin/env python

import os
import time
import socket
import subprocess
import vice_monitor

sargon_prg = "vic20-sargon-ii-chess/PRG/SargonII-2000.prg"

MON_PORT = 6510
MON_HOST = "127.0.0.1"

# Unprintable character codes for keyboard buffer using c-style hex escapes per vice manual
CHR_F1 = '\\x85'
CHR_RETURN = '\\x0d'
CHR_CURSOR_RIGHT = '\\x1d'
CHR_CURSOR_DOWN = '\\x11'


def vmon(command):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((MON_HOST, MON_PORT))
        # TODO ? does this block or do we need to specify a flag to make it block?
        s.sendall(command.encode('utf-8'))
        data = s.recv(1024)
        return data.decode('utf-8')


def send_keys(keys):
    """
    Sets the keybuffer of the guest machine to the given string.
    Use c-style hex escapes for non-glyph keys
    """
    return vmon(f"keybuf {keys}\n")


def main():

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
    time.sleep(6)

    print("centering screen")
    send_keys(CHR_CURSOR_RIGHT * 7 + CHR_CURSOR_DOWN * 8)
    return
    print("starting game as white on level 0")
    send_keys(CHR_F1)
    send_keys("gw0")

    # TODO wait for game board ready to start and white's move

    print("entering white move d2-d4")
    send_keys(f"d2-d4{CHR_RETURN}")

    # TODO figure out how to wait for the move to happen

    print("sleeping")
    time.sleep(5)
    # use binarymonitor to get registers
    print("registers:")
    print(vice_monitor.get_registers())

    print(vice_monitor.read_memory(0x2000, 0x2020))

    # print("sleeping before quit")
    # time.sleep(10)
    # print(send_keys("quit"))

if __name__ == "__main__":
    main()
