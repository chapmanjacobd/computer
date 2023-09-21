# Defined interactively
function pperf
    ltrace -fcp $argv
    # valgrind --tool=cachegrind $argv
    # perf stat -e instructions,cache-misses -p $argv
end
