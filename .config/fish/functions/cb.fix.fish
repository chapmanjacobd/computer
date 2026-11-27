# Defined interactively
function cb.fix
    string replace --all --regex '\s{2,}' '\n' -- (cb) | cb
end
