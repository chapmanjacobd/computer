# Defined interactively
function go.deps.upgrade
    go get -u -t ./...
    go mod tidy
end
