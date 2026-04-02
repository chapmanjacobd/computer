# Defined in /home/xk/.config/fish/functions/disco.dev.fish @ line 2, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function shrink.dev
    ~/github/xk/shrink
    go run -tags fts5 ./cmd/shrink $argv
end
