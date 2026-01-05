# Defined interactively
function ps.io
    sudo bpftrace -e 'tracepoint:block:block_rq_issue { @bytes[comm] = sum(args.bytes); } interval:s:1 { exit(); }' | grep -vE 'kworker|btrfs-transacti' | bpftrace_human_size.awk
end
