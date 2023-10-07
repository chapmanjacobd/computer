# Defined interactively
function mkdir
    if path extension $argv >/dev/null
        command mkdir (path dirname $argv)
    else
        command mkdir $argv
    end
end
