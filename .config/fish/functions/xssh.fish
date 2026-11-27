# Defined interactively
function xssh --wraps='ssh'
    ssh -O exit $argv
    ssh -X $argv
end
