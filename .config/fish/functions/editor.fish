# Defined via `source`
function editor
    if set -q DISPLAY
        $VISUAL $argv
    else
        $EDITOR $argv
    end
end
