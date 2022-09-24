# Defined interactively
function repeal
    while not fish -c (string join -- ' ' (string escape -- $argv))
        and :
    end
end
