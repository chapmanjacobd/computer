# Defined interactively
function goformat
    gofmt -s -w -e .
    goimports -w -e .
    gofumpt -w .
    gci write .
end
