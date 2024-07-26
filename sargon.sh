#!/usr/bin/env bash

# starts sargon ii on vice vic 20 emulator

#
export sargon_cart="sargon-a0.crt"
export sargon_prg="SargonII-2000.prg"

export monitor_port="6510"
export monitor_host="127.0.0.1"
export monitor_address="ip4://$monitor_host:$monitor_port"

# character codes for sending to keyboard buffer
export CHR_F1='\x85'
export CHR_RETURN='\x0d'

function vmon() {
  echo "$*" | nc $monitor_host $monitor_port
}

function send_keys() {
  # TODO do we need to set the keyboard buffer size?
  vmon "keybuf $*"
}

if [[ $1 == "cart" && -f "$sargon_cart" ]]; then
    xvic -remotemonitor -remotemonitoraddress "$monitor_address" \
        -cartA "$sargon_cart" \
        >vice.out.log &

    echo waiting for cart to boot
    sleep 3

else
    xvic -remotemonitor -remotemonitoraddress "$monitor_address" \
        -memory 8k \
        -autostartprgmode 1 \
        "$sargon_prg" \
        >vice.out.log &

    echo waiting for prg to load
    sleep 6
fi

# entering keys with the monitor seems to work for normal chars
# using the keybuf command which fills the keyboard buffer with the 
# given string. Non-printable chars are escaped with a \xhh sequence
# where hh is a hex number corresponding to the CHR$ value as described
# in the Vic-20 Programmer's Reference Guide.

# type <f1> to start then
# g for game, s for setup then if g
# b for black, w for white then
# level: 0-6

# f1 is char code 133 (0x85) as specified in Vic-20 manual by $CHR()
# return is char code 13 (0x0d).
# Note there is also shift-return: 141 (0x8d)

echo starting game as white on level 0
send_keys $CHR_F1
send_keys "gw0"
echo entering white move d2-d4
send_keys "d2-d4$CHR_RETURN"


