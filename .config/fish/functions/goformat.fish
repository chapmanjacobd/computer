# Defined interactively
function goformat
    gofmt -swe
    goimports -wve
end
