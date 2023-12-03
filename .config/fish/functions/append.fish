# Defined interactively
function append
    echo $argv[2..-1] >>$argv[1]
end
