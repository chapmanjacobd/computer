# Defined interactively
function files.lines.truncate
    set qty $argv[1]
    set f $argv[2..-1]

    tail -n $qty "$f"
    head -n -$qty "$f" | sponge "$f"
end
