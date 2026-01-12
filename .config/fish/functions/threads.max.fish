# Defined interactively
function threads.max
    set -l mem_chunks (math -s 0 (printf "%d/(1024 * 1024 * $argv)" (grep MemAvailable /proc/meminfo | awk '{print $2}')))
    set -l nproc (nproc)

    if test $nproc -gt $mem_chunks
        echo $mem_chunks
    else
        echo $nproc
    end
end
