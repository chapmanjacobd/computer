# Defined interactively
function trash-empty-no-snapshot
    filter_opts $argv

    if test -z "$args"
        echo Error! No mount points passed as args
        return 1
    end

    trash-size
    trash-list >>~/.local/share/trashed.txt

    if contains -- -f $opts; or gum confirm --default=no 'Empty trash?'
        command trash-empty-no-snapshot -f
    end
end
