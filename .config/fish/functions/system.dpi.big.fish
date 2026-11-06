# Defined in /home/xk/.config/fish/functions/system.dpi.small.fish @ line 1, copied in /home/xk/.config/fish/functions/funccp.fish @ line 3
function system.dpi.big
    if test "$XDG_SESSION_TYPE" = x11
        xrandr --dpi 192
    end
    echo 'Xft.dpi: 192' | xrdb -override
    set -l changes
    for output in (_kscreen_outputs)
        set -a changes output.$output.scale.2
    end
    if test (count $changes) -gt 0
        kscreen-doctor $changes
    end
    kwriteconfig6 --file kdeglobals --group KScreen --key ScaleFactor 2
    sed -i -E 's/^Gdk\/UnscaledDPI .*/Gdk\/UnscaledDPI 196608/' ~/.config/xsettingsd/xsettingsd.conf

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

    qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript 'panels().forEach(function(panel) { if (panel.location === "bottom" && panel.screen >= 0) panel.height = 64; });'

    kwin.restart
end
