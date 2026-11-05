function system.dpi.small
    if test "$XDG_SESSION_TYPE" = x11
        xrandr --dpi 128
    end
    echo 'Xft.dpi: 128' | xrdb -override
    set -l changes
    for output in (_kscreen_outputs)
        set -a changes output.$output.scale.1
    end
    if test (count $changes) -gt 0
        kscreen-doctor $changes
    end
    kwriteconfig6 --file kdeglobals --group KScreen --key ScaleFactor 1
    sed -i -E 's/^Gdk\/UnscaledDPI .*/Gdk\/UnscaledDPI 131072/' ~/.config/xsettingsd/xsettingsd.conf

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

    qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript 'panels().forEach(function(panel) { if (panel.location === "bottom" && panel.screen >= 0) panel.height = 42; });'
end
