function kde.clock.isodate --description 'Set every KDE Digital Clock widget to ISO Date'
    qdbus org.kde.plasmashell /PlasmaShell org.kde.PlasmaShell.evaluateScript '
        var clocks = [];
        function fix(containment) {
            containment.widgets().forEach(function(widget) {
                if (widget.type === "org.kde.plasma.digitalclock") {
                    widget.currentConfigGroup = ["Appearance"];
                    widget.writeConfig("dateFormat", "isoDate");
                    widget.reloadConfig();
                    clocks.push(widget.id);
                }
            });
        }
        panels().forEach(fix);
        desktops().forEach(fix);
        print("ISO date set on Digital Clock widgets: " + clocks.join(", "));
    '
end
