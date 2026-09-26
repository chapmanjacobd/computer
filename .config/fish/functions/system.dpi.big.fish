# Defined in /home/xk/.config/fish/functions/system.dpi.small.fish @ line 1, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function system.dpi.big
    xrandr --dpi 192
    echo 'Xft.dpi: 192' | xrdb -override
    sed -i 's/ScaleFactor=1/ScaleFactor=2/' ~/.config/kdeglobals ~/.config/xsettingsd/xsettingsd.conf

    set fopt layout.css.devPixelsPerPx
    set fset 1.7

    for profile in ~/.mozilla/firefox/*/
        set -l target "$profile/user.js"
        if test -f $target; and grep -q "user_pref(\"$fopt\"," $target
            sed -i "s/user_pref(\"$fopt\",.*/user_pref(\"$fopt\",$fset);/" $target
        else
            echo "user_pref(\"$fopt\",$fset);" >>$target
        end
    end
end
