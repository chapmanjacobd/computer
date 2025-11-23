# Defined interactively
function goformat
    staticcheck ./...
    go vet -c=1 ./...
    gofmt -s -w -e .
    goimports -w -e .
    gofumpt -w .
    gci write .
end
