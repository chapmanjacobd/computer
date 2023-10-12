# Defined interactively
function create_lock_file
    set lockfile "/tmp/$argv.lock"

    if test -e $lockfile
        echo "Lock file $lockfile already exists."
        return 1
    else
        touch $lockfile
        return 0
    end
end
