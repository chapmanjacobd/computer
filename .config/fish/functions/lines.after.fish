# Defined interactively
function lines.after --argument pattern
    sed -n '/'$pattern'/,$p' $argv[2]
end
