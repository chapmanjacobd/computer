# Defined interactively
function erm
    echo -n $argv | string escape | xargs rm
end
