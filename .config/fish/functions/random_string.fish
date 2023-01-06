# Defined interactively
function random_string --argument len
    cat /dev/urandom | tr -dc a-zA-Z0-9 | head -c $len
end
