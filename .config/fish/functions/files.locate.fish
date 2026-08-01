# Defined interactively
function files.locate
    print $argv | xargs -I{} find "{}" -type f
end
