# Defined via `source`
function ps.tail
    sudo bpftrace -e 'tracepoint:syscalls:sys_enter_exec*{ printf("pid: %d, cmd: %s, args: ", pid, comm); join(args->argv); }'
end
