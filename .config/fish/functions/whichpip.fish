# Defined interactively
function whichpip
    pip list -v $argv | grep -i $argv | choose 2
end
