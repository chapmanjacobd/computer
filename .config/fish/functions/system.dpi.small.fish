function system.dpi.small
    xrandr --dpi 96
    echo 'Xft.dpi: 96' | xrdb -override
    sed -i 's/ScaleFactor=2/ScaleFactor=1' ~/.config/kdeglobals
    set fopt layout.css.devPixelsPerPx
    set fset 1
    cd ~/.mozilla/firefox/8eqln2tw.default/
    sed -i 's/user_pref("'$fopt'",.*);/user_pref("'$fopt'","'$fset'");/' user.js
    grep -q $fopt user.js || echo "user_pref(\"$fopt\",$fset);" >>user.js
end
