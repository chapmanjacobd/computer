# Defined interactively
function random.timestamp
    od --read-bytes=4 --address-radix=n --format=u4 /dev/random | awk '{print $1$2}'
end
