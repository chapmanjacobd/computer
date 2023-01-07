# Defined interactively
function filels
    command ls --zero $argv | xargs -0 -I FILE file -b FILE
end
