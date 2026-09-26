function system.dpi.small
    xrandr --dpi 96
    echo 'Xft.dpi: 96' | xrdb -override
    sed -i 's/ScaleFactor=2/ScaleFactor=1' ~/.config/kdeglobals ~/.config/xsettingsd/xsettingsd.conf

    set fopt layout.css.devPixelsPerPx
    set fset 1.1

    for profile in ~/.mozilla/firefox/*/
        set -l target "$profile/user.js"
        if test -f $target; and grep -q "user_pref(\"$fopt\"," $target
            sed -i "s/user_pref(\"$fopt\",.*/user_pref(\"$fopt\",$fset);/" $target
        else
            echo "user_pref(\"$fopt\",$fset);" >>$target
        end
    end
end
