# Defined interactively
function match-first-tail --argument pattern
    sed -n '/'$pattern'/,$p' $argv[2]
end
