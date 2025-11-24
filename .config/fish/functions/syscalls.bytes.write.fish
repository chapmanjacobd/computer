# Defined via `source`
function syscalls.bytes.write
    #sudo bpftrace -e 'tracepoint:syscalls:sys_exit_write /args.ret/ { @[comm] = sum(args.ret); }'
    sudo bpftrace -e 'tracepoint:syscalls:sys_exit_write /args.ret/ { @writes_sum[comm] = sum(args.ret); } interval:s:5 { print(@writes_sum); }'
end
