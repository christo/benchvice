#!/usr/bin/env zsh

# starts sargon ii on vice vic 20 emulator
# depends on nc, xvic (from vice)

source source.sh

xvic -remotemonitor -remotemonitoraddress "$monitor_address" \
    -binarymonitor \
    -config "vice.config" \
    -memory 8k \
    -autostartprgmode 1 \
    "$sargon_prg" \
    >vice.out.log &



echo waiting for prg to load
sleep 6
echo centering screen
shift_right=$(printf "%0.s$CHR_CURSOR_RIGHT" {1..7})
shift_down=$(printf "%0.s$CHR_CURSOR_DOWN" {1..10})
send_keys "${shift_right}${shift_down}"
#dump_mem_wait "1post_screen_centre.mem"
echo starting game as white on level 0
send_keys $CHR_F1
send_keys "gw0"
#dump_mem_wait "2post_game_select.mem"
echo entering white move d2-d4
send_keys "d2-d4$CHR_RETURN"
#dump_mem_wait "3post_move.mem"


is_human_turn
RV=$?
exit $RV
