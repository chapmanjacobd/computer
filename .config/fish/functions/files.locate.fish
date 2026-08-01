# Defined via `source`
function files.locate
    if set -q argv[1]
        print $argv | xargs -I{} find "{}" -type f
    else
        xargs -I{} find "{}" -type f
    end
end
