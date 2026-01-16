# Defined interactively
function catar
    argparse h/help -- $argv
    or return

    if set -q _flag_help; or not set -q argv[1]
        echo "Usage: catar <archive.tar>"
        return 0
    end

    set -l args (printf '%s\n' $argv)

    for archive in $args
        for entry in (tar -tf $archive)
            echo "--- $entry ---"
            tar -xf $archive $entry -O
            echo
        end
    end
end
