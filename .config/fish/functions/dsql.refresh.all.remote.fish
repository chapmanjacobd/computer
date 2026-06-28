# Defined interactively, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function dsql.refresh.all.remote
    for s in $servers
        dsql.refresh.remote $s
    end
end
