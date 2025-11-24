function system.dpi.big
    xrandr --dpi 192
    echo 'Xft.dpi: 192' | xrdb -override
    sed -i 's/ScaleFactor=1/ScaleFactor=2' ~/.config/kdeglobals
    set fopt layout.css.devPixelsPerPx
    set fset 1.7
    cd ~/.mozilla/firefox/8eqln2tw.coalesce/
    sed -i 's/user_pref("'$fopt'",.*);/user_pref("'$fopt'","'$fset'");/' user.js
    grep -q $fopt user.js || echo "user_pref(\"$fopt\",$fset);" >>user.js
end
