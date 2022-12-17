# Defined interactively
function ls --description 'An alias for exa with some defaults'
    if status --is-interactive
        if test -d .git
            exa --git --long --header --classify --sort=type --group-directories-first $argv
        else
            exa --long --header --classify --sort=none --group-directories-first $argv
        end
    else
        /usr/bin/ls --sort=none $argv
    end
end
