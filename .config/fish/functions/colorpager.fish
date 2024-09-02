# Defined interactively
function colorpager
    script -q -c (string join -- ' ' (string escape -- $argv)) /dev/null | less -R
end
