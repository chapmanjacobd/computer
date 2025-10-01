# Defined interactively
function allqb
    set -l all_failed true

    for s in 127.0.0.1:8080 backup:8888 r730xd:8888 len:8888 hk:8888
        $argv --host $s

        if test $status -eq 0
            set all_failed false
        end
    end

    if $all_failed
        return $status
    else
        return 0
    end
end
