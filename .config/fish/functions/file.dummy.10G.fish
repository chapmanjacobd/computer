# Defined interactively
function file.dummy.10G
    dd if=/dev/urandom of="$argv" bs=1M count=10240 status=progress
end
