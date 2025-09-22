# Defined via `source`
function syscalls_bytes_read
    #sudo bpftrace -e 'tracepoint:syscalls:sys_exit_read /args.ret/ { @[comm] = sum(args.ret); }'
    sudo bpftrace -e 'tracepoint:syscalls:sys_exit_read /args.ret/ { @reads_sum[comm] = sum(args.ret); } interval:s:5 { print(@reads_sum); }'
end
