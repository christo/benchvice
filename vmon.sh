#!/usr/bin/env bash

# starts sargon ii on vice vic 20 emulator
# depends on nc, xvic (from vice)

export sargon_prg="vic20-sargon-ii-chess/PRG/SargonII-2000.prg"

export monitor_port="6510"
export monitor_host="127.0.0.1"
export monitor_address="ip4://$monitor_host:$monitor_port"

# unprintable character codes for sending to keyboard buffer
export CHR_F1='\x85'
export CHR_RETURN='\x0d'
export CHR_CURSOR_RIGHT='\x1d'
export CHR_CURSOR_DOWN='\x11'


# sends args as monitor command, results to stdout
function vmon() {
  echo "$*" | nc $monitor_host $monitor_port
}

# sends args as keys
function send_keys() {
  # TODO do we need to set the keyboard buffer size?
  vmon "keybuf $*"
}

function screenshot() {
  vmon "screenshot \"$1\" 2"
}

# dumps memory to file $1
function dump_mem() {
  vmon "s \"$1\" 0 0000 ffff"
}

function dump_mem_wait() {
  sleep 5
  screenshot "$1.png"
  dump_mem "$1"
  hexdump -vC "$1" > "$1.hex"
  sleep 5
}

xvic -remotemonitor -remotemonitoraddress "$monitor_address" \
    -binarymonitor \
    -memory 8k \
    -autostartprgmode 1 \
    "$sargon_prg" \
    >vice.out.log &


dump_mem_wait "1pre_load.mem"
echo waiting for prg to load
sleep 6
dump_mem_wait "2post_load.mem"
echo centering screen
for ((i=0; i<7; i++)); do
    send_keys "$CHR_CURSOR_RIGHT$CHR_CURSOR_DOWN"
done
send_keys "$CHR_CURSOR_DOWN$CHR_CURSOR_DOWN"
dump_mem_wait "3post_screen_centre.mem"
echo starting game as white on level 0
send_keys $CHR_F1
dump_mem_wait "4post_game_f1.mem"
send_keys "gw0"
dump_mem_wait "5post_game_select.mem"
echo entering white move d2-d4
send_keys "d2-d4$CHR_RETURN"
dump_mem_wait "6post_move.mem"
vmon "quit"

