# Defined in /home/xk/.config/fish/functions/dsql.refresh.fish @ line 2, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function disco.add
    set joblog (mktemp)
    for m in $argv[2..-1]
        echo disco add $argv[1] "$m"
    end | parallel --shuf --joblog $joblog
    parallel --retry-failed --joblog $joblog -j1
end
