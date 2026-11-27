# Defined interactively
function bcrypt --wraps='mkpasswd'
    mkpasswd --method=bcrypt --rounds=12 $argv
end
