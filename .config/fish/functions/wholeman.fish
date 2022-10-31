# Defined interactively
function wholeman
    set short (tldr $argv)
    set tips (cheat $argv)
    set long (man $argv)
    set sl (string length $short)
    if test $sl -lt 100
        echo $tips $long
    else
        echo $tips $short
    end
end
