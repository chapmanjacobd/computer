# Defined interactively
function qdbus
    if command -sq qdbus-qt6
        qdbus-qt6 $argv
    else
        qdbus $argv
    end
end
