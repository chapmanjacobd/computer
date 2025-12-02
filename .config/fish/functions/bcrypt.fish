# Defined interactively
function bcrypt
    mkpasswd --method=bcrypt --rounds=12 $argv
end
