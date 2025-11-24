# Defined interactively
function server.ssh --argument pc
    echo $pc
    ssh $pc $argv[2..-1]
    echo
end
