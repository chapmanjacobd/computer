# Defined interactively
function ls -w eza
    echo Why not try Ctrl+Alt+F?

    if status --is-interactive
        if has_git_dir $argv; and not string match -q '/net/*' $argv; and not string match -q '/net/*' $PWD
            eza --git --long --header --classify --sort=type --group-directories-first $argv
        else
            eza --long --header --classify --sort=none --group-directories-first $argv
        end
    else
        /usr/bin/ls --sort=none $argv
    end
end
