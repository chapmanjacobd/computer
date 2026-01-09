# Defined interactively
function shrink
    lb shrink -vy $argv --move ../processed/ --move-broken ../processed-broken/ --delete-unplayable
end
