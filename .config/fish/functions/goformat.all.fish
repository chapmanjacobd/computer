# Defined in /home/xk/.config/fish/functions/goformat.fish @ line 2, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function goformat.all
    staticcheck ./...
    go vet -c=1 ./...
    gofmt -s -w -e .
    goimports -w -e .
    gofumpt -w .
    gci write .
end
