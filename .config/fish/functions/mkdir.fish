# Defined interactively
function mkdir
    if path extension $argv >/dev/null
        command mkdir -p (path dirname $argv)
    else
        command mkdir -p $argv
    end
end
