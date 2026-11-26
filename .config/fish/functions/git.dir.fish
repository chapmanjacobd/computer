function git.dir
    if test (count $argv) -eq 0
        if test -d .git
            return 0 # True (git dir found)
        else
            return 1 # False (git dir not found)
        end
    else
        if test -d "$argv/.git"
            return 0 # True
        else
            return 1 # False
        end
    end
end
