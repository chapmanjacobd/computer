# Defined interactively
function chmod.reset
    fd -td $argv -x chmod (math 777-(umask))
    fd -tf $argv -x chmod (math 666-(umask))
end
