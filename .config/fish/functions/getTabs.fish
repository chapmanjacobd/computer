function getTabs
    head -30 ~/Documents/tabs.txt | xclip -selection c
    sed -i -e 1,30d ~/Documents/tabs.txt
end
