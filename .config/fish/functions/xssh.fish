# Defined interactively
function xssh
    ssh -O exit $argv
    ssh -X $argv
end
