# Defined via `source`
function files.locate
    if test -t 0
        print $argv | xargs -I{} find "{}" -type f
    else
        xargs -I{} find "{}" -type f
    end
end
