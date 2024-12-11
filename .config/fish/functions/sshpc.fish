# Defined interactively
function sshpc --argument pc
    echo $pc
    ssh $pc $argv[2..-1]
    echo
end
