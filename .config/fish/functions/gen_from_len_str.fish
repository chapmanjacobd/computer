# Defined via `source`
function gen_from_len_str
    head -(math "$argv*30")c /dev/urandom | tr -cd '[:alnum:]' | head -"$argv"c
end
