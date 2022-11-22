# Defined interactively
function dptmp
    echo $argv | sed 's|.*temp/\(.*\)|tmp/\1|'
end
