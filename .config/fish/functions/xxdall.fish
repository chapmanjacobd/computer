# Defined interactively
function xxdall
    for f in (fd -HI -tf)
        echo $f
        hexyl $f
    end | ov
end
