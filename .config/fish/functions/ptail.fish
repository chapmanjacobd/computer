# Defined interactively
function ptail
    sudo bpftrace -e 'tracepoint:syscalls:sys_enter_exec*{ printf("pid: %d, comm: %s, args: ", pid, comm); join(args->argv); }'
end
