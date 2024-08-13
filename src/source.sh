
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

# fancy dump
function dump_mem_wait() {
  sleep 5
  screenshot "$1.png"
  vmon "screen " >"$1.scr.txt"
  dump_mem "$1"
  hexdump -vC "$1" > "$1.hex"
  sleep 5
}

# read memory locations holding human colour and current turn colour
# if they are the same, it's the human's turn
function is_human_turn() {
  human_current=$( echo "m 15 16" | nc $monitor_host $monitor_port | head -n 1 | cut -c 20,21,23,24)
  human=${human_current[1,2]}
  current=${human_current[3,4]}
  if [[ "$human" == "$current" ]]; then
    return 1
  else
    return 0
  fi
}
