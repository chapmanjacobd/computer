function lines.cut10.cb
    head -10 "$argv" | xclip -selection c
    sed -i -e 1,10d "$argv"
end
