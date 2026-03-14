# Defined interactively
function disco.dev
    go run -tags bleve ./cmd/disco serve -v --dev $argv
end
