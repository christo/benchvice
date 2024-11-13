#!/usr/bin/env zsh

# WIP automated test to solve the problem of connecting to the monitor
# to read the machine memory in a concurrency safe way.


# if xvic is running exit and fail

SCRIPT_DIR=$(dirname "$0")
source "$SCRIPT_DIR/source.sh"

function sargon_vice() {
  if [[ $(pgrep xvic) ]]; then
    echo "xvic already running"
    exit 1
  fi
  xvic -remotemonitor -remotemonitoraddress "$monitor_address" \
      -binarymonitor \
      -debug \
      -config "$SCRIPT_DIR/../vice.config" \
      -memory 8k \
      -autostartprgmode 1 \
      "$SCRIPT_DIR/../$sargon_prg" \
      >"$SCRIPT_DIR/../vice.out.log" &
}

echo starting xvic

sargon_vice

