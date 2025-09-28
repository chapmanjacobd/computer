# Defined interactively
function blockdevices
    udevadm info /sys/block/* --query=property | grep -E '^(DEVNAME|USEC_INITIALIZED)' | paste -d ' ' - - | grep -vE '^DEVNAME=/dev/(loop|zram)' | sort -k 4 -nr | awk -F'[ ="]' '{print $2}'
end
