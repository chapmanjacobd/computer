# Defined interactively
function git-ls-filter --description 'Filter git ls-files -v by status character'
    set -l target_status $argv[1]
    set -e argv[1]

    git ls-files -v $argv | while read -l line
        set -l status_char (string sub -l 1 -- $line)
        if test "$status_char" = "$target_status"
            # Strip status char and the following space
            string sub -s 3 -- $line
        end
    end
end
