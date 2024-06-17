# Defined interactively
function remove_empty_directories
    if set -q argv[1]
        $argv
    end
    bfs -type d -empty -delete
end
