# Defined interactively
function lines.count
    if not set -q argv[1]
        cat | count
        return
    end

    for s in $argv
        wc -l "$s" | cut -f1 -d' '
    end
end
