# Defined interactively
function with_lock
    if not create_lock_file $argv
        echo "$argv already running..."
        return 1
    end
    eval $argv
    clear_lock_file $argv
end
