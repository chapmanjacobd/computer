# Defined interactively
function cattrash
    cat $argv/*
    trash-put $argv
end
