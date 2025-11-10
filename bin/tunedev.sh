#!/bin/bash

set -Eeuo pipefail

declare -A HDD_SETTINGS
HDD_SETTINGS=(
    ["scheduler"]="bfq"
    ["nr_requests"]="4"
    ["iosched/back_seek_max"]="32000"
    ["iosched/back_seek_penalty"]="3"
    ["iosched/fifo_expire_sync"]="80"
    ["iosched/fifo_expire_async"]="1000"
    ["iosched/slice_idle_us"]="5300"
    ["iosched/low_latency"]="1"
    ["iosched/timeout_sync"]="200"
    ["iosched/max_budget"]="0"
    ["iosched/strict_guarantees"]="1"
)

declare -A SSD_OVERRIDES
SSD_OVERRIDES=(
    ["nr_requests"]="36"
    ["iosched/back_seek_penalty"]="1"
    ["iosched/slice_idle_us"]="16"
    ["iosched/fifo_expire_sync"]="10"
    ["iosched/fifo_expire_async"]="250"
    ["iosched/timeout_sync"]="10"
    ["iosched/strict_guarantees"]="0"
)

if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root"
   exit 1
fi

modprobe bfq

DRIVE_PATH=$(find /sys/block -maxdepth 1 -regex '/sys/block/\(sd[a-z]\|nvme[0-9]n[0-9]\)' -printf "%P\n" 2>/dev/null | fzf --prompt="Select a block device to tune: " --height 10 --border)

if [[ -z "$DRIVE_PATH" ]]; then
    echo "No drive selected"
    exit 2
fi

DEVICE_DIR="/sys/block/$DRIVE_PATH/queue"
IS_ROTATIONAL=$(cat "$DEVICE_DIR/rotational" 2>/dev/null)

SETTINGS_TO_APPLY=("${!HDD_SETTINGS[@]}")
if [[ "$IS_ROTATIONAL" == "0" ]]; then
    echo "Applying **SSD** overrides."
    for KEY in "${!SSD_OVERRIDES[@]}"; do
        HDD_SETTINGS["$KEY"]="${SSD_OVERRIDES["$KEY"]}"
    done
fi

get_current_value() {
    local FILE="$1"
    if [[ -f "$FILE" ]]; then
        cat "$FILE"
    fi
}

# Apply settings
for FILE_NAME in "${!HDD_SETTINGS[@]}"; do
    NEW_VALUE="${HDD_SETTINGS[$FILE_NAME]}"

    FULL_PATH="$DEVICE_DIR/$FILE_NAME"
    if [[ ! -f "$FULL_PATH" ]]; then
        continue
    fi

    CURRENT_VALUE=$(get_current_value "$FULL_PATH")
    printf "  - %-25s | Current: **%s**" "$FILE_NAME" "$CURRENT_VALUE"

    echo "$NEW_VALUE" > "$FULL_PATH" 2>/dev/null

    APPLIED_VALUE=$(get_current_value "$FULL_PATH")
    if [[ "$CURRENT_VALUE" != "$APPLIED_VALUE" ]]; then
        printf " -> Changed to: **%s**\n" "$APPLIED_VALUE"
    fi
done
