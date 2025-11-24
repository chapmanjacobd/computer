# Defined interactively
function xxd.all
    for f in (fd -HI -tf)
        echo $f
        hexyl $f
    end | ov
end
