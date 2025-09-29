# Defined interactively
function goformat
    go vet -c=1 ./...
    gofmt -s -w -e .
    goimports -w -e .
    gofumpt -w .
    gci write .
end
