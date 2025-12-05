# Defined interactively
function goformat
    staticcheck $argv
    go vet -c=1 $argv
    gofmt -s -w -e $argv
    goimports -w -e $argv
    gofumpt -w $argv
    gci write $argv
end
