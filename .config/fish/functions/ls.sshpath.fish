# Defined interactively
function ls.sshpath
    set l (string split -r ":" $argv)

    ssh -t $l[1] eza --long --header --classify --sort=none --group-directories-first --sort=name $l[2]
end
