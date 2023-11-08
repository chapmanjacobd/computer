# Defined via `source`
function ptail
    sudo bpftrace -e 'tracepoint:syscalls:sys_enter_exec*{ printf("pid: %d, cmd: %s, args: ", pid, comm); join(args->argv); }'
end
