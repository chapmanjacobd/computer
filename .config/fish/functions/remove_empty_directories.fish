# Defined interactively
function remove_empty_directories
    if set -q argv[1]
        $argv
    end
    yes | bfs -type d -exec bfs -f {} -not -type d -exit 1 \; -prune -ok bfs -f {} -type d -delete \;
end
