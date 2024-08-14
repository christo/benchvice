#!/usr/bin/env zsh

# starts sargon ii on vice vic 20 emulator
# depends on nc, xvic (from vice)

SCRIPT_DIR=$(dirname "$0")
source "$SCRIPT_DIR/source.sh"

xvic -remotemonitor -remotemonitoraddress "$monitor_address" \
      -binarymonitor \
      -config "$SCRIPT_DIR/../vice.config" \
      -memory 8k \
      -autostartprgmode 1 \
      "$SCRIPT_DIR/../$sargon_prg" \
      >"$SCRIPT_DIR/../vice.out.log" &

exit

echo waiting for prg to load
sleep 6
echo centering screen
shift_right=$(printf "%0.s$CHR_CURSOR_RIGHT" {1..7})
shift_down=$(printf "%0.s$CHR_CURSOR_DOWN" {1..10})
send_keys "${shift_right}${shift_down}"
sleep 1
#dump_mem_wait "1post_screen_centre.mem"
echo starting game as white on level 0
send_keys $CHR_F1
send_keys "gw0"
sleep 1
#dump_mem_wait "2post_game_select.mem"
echo entering white move d2-d4
send_keys "d2-d4$CHR_RETURN"
#dump_mem_wait "3post_move.mem"
sleep 1
send_keys "c1-f4$CHR_RETURN"

#is_human_turn
RV=$?
exit $RV
