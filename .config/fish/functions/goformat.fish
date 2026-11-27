# Defined interactively
function goformat --wraps='gofmt'
    staticcheck $argv
    go vet -c=1 $argv
    gofmt -s -w -e $argv
    go fix $argv
    goimports -w -e $argv
    gofumpt -w $argv
    gci write $argv
end
