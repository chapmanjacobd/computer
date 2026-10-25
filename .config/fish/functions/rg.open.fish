# Defined in /home/xk/.config/fish/functions/fd.open.fish @ line 2, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function rg.open --argument-names prog
    for f in (rg --files-with-matches $argv[2..-1])
        $prog $f
    end
end
