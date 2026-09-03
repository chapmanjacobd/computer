function rm.secure
    set -l files
    set -l dirs

    for target in $argv
        if test -d $target
            set -a dirs $target
        else if test -f $target
            set -a files $target
        else
            echo "rm.secure: $target: not a file or directory" >&2
        end
    end

    for dir in $dirs
        set -a files (find $dir -type f)
    end

    if test (count $files) -eq 0
        echo "rm.secure: nothing to shred" >&2
        return 1
    end

    shred -u -z -n 3 $files

    for dir in $dirs
        rm -rf $dir
    end

    for target_mount in (df --output=target $files $dirs | tail -n +2 | sort -u)
        sudo fstrim -v "$target_mount"
    end
end
