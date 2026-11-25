function lines.cut10.cb
    head -10 "$argv" | cb
    sed -i -e 1,10d "$argv"
end
