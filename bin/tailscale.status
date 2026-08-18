#!/bin/bash
tailscale status --json | jq -r '.Self,.Peer[] | (try .Tags[] catch "-") + " " + .TailscaleIPs[] + " " + .HostName + " " + .DNSName + " " + (if .Relay == "" then "-" else .Relay end) + " XXX" + (.Online|tostring) + "XXX " + .OS' | sort -V | column -t | \
    while read l; do
        line=$(echo "$l" | sed 's/ XXXtrueXXX /\\033[0;32m ✅\\033[0m/ ; s/ XXXfalseXXX /\\033[0;31m ❌ \\033[0m/')
        echo -e "$line" $(tailscale whois --json $(echo $line | cut -d' ' -f2) | jq -r '.Node.Hostinfo | .Distro + " " + .DistroVersion + " " + .DeviceModel');
    done
