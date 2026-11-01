#!/bin/bash
# 
# Direct file transfer over a ethernet patch cable: no switch needed.
#
# Linux only, requires socat.

set -eo pipefail

echoerr() { echo "$@" 1>&2; }

if [[ $3 == "" ]]; then
  echoerr "Usage: $0 <iface> tx/rx <filename>"
  echoerr "Send files over an ethernet cable, requires root."
  echoerr ""
  echoerr "Receiving side should be started first."
  exit 1
fi

export iface=$1

# Clear out existing addresses before configuring our own
ip address flush $iface

if [[ $2 == "tx" ]]; then
  # IP configuration (disable duplicate address detection to avoid weird stalls)
  ip address add dev "$iface" fd42:dead:beef::1/48 nodad
  ip link set dev "$iface" up
  # Wait for phy to configure...
  while ! ip link show "$iface" | grep LOWER_UP -q; do
    echoerr "Waiting for interface to come up..."
    sleep 1
  done
  # ... and send the file!
  echoerr "Connecting..."
  socat - 'TCP6-CONNECT:[fd42:dead:beef::2]:1234' < "$3"
elif [[ $2 == "rx" ]]; then
  # IP configuration
  ip address add dev "$iface" fd42:dead:beef::2/48 nodad
  ip link set dev "$iface" up
  # Listen on the network for our file
  # Using dd to provide progress and speed indications to stderr
  echoerr "Waiting for file..."
  socat - TCP6-LISTEN:1234 | dd status=progress bs=1M > "$3"
  echo "All done!"
else
  echoerr "Invalid subcommand."
  exit 1
fi

# Clean up
ip link set dev $iface down
ip address flush $iface
