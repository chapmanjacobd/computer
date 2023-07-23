# Defined interactively
function pperf
    ltrace -fcp $argv
    # perf stat -e instructions,cache-misses -p $argv
end
