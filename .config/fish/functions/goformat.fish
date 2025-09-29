# Defined interactively
function goformat
    go vet ./...
    gofmt -s -w -e .
    goimports -w -e .
    gofumpt -w .
    gci write .
end
