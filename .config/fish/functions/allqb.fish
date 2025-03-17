# Defined interactively
function allqb
    for s in 127.0.0.1:8080 backup:8888 r730xd:8888 len:8888 hk:8888
        $argv --host $s
    end
end
