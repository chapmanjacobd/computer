# Defined interactively
function r730xd.fans
    ipmitool -I lanplus -H $argv[2] -U root -P $argv[1] raw 0x30 0x30 0x01 0x00
    ipmitool -I lanplus -H $argv[2] -U root -P $argv[1] raw 0x30 0x30 0x02 0xff $(printf '0x%02x' 33)
end
