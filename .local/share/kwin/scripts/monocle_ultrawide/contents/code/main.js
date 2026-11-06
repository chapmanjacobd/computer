"use strict";

const OUTPUT_NAME = "dp-1";
const SIDE_GAP = 700;
const ARRANGE_DELAY = 50;
const IGNORED_CLASSES = new Set([
    "krunner",
    "yakuake",
    "spectacle",
    "kded5",
    "xwaylandvideobridge",
    "plasmashell",
    "ksplashqml",
    "org.kde.plasmashell",
    "org.kde.polkit-kde-authentication-agent-1",
    "org.kde.kruler",
    "kruler",
    "kwin_wayland",
    "ksmserver-logout-greeter",
]);

function text(value) {
    return value == null ? "" : String(value).toLowerCase();
}

function contains(value, needle) {
    return text(value).indexOf(needle) !== -1;
}

function isIgnored(window) {
    if (!window || window.deleted || !window.normalWindow || window.popupWindow ||
        window.hidden || window.specialWindow || window.fullScreen) {
        return true;
    }

    if (IGNORED_CLASSES.has(text(window.resourceClass)) ||
        contains(window.caption, "mpv") ||
        contains(window.windowRole, "quake")) {
        return true;
    }

    return window.keepAbove || window.keepBelow ||
        window.dialog || window.splash || window.utility ||
        window.transient || window.modal || window.resizeable === false;
}

function isOnCurrentDesktop(window) {
    return window.onAllDesktops ||
        window.desktops.length === 0 ||
        window.desktops.includes(workspace.currentDesktop);
}

function isOnCurrentActivity(window) {
    return window.activities.length === 0 ||
        window.activities.includes(workspace.currentActivity);
}

function isManaged(window) {
    return !isIgnored(window) &&
        window.output &&
        text(window.output.name) === OUTPUT_NAME &&
        !window.minimized &&
        isOnCurrentDesktop(window) &&
        isOnCurrentActivity(window);
}

const managedWindows = new Set();

function arrange() {
    for (const window of workspace.windowList()) {
        if (!isManaged(window)) {
            if (!managedWindows.has(window)) {
                continue;
            }

            if (!window.output || text(window.output.name) === OUTPUT_NAME) {
                if (isIgnored(window)) {
                    managedWindows.delete(window);
                }
                continue;
            }

            if (!isIgnored(window) && window.maximizable && !window.fullScreen) {
                window.setMaximize(true, true);
            }
            managedWindows.delete(window);
            continue;
        }

        managedWindows.add(window);

        if (window.maximizeMode > 0) {
            window.setMaximize(false, false);
        }

        const geometry = workspace.clientArea(KWin.FullArea, window);
        const width = geometry.width - SIDE_GAP * 2;
        if (width <= 0) {
            continue;
        }

        window.frameGeometry = {
            x: geometry.x + SIDE_GAP,
            y: geometry.y,
            width: width,
            height: geometry.height,
        };
    }
}

let arrangePending = false;
const arrangeTimer = new QTimer();
arrangeTimer.interval = ARRANGE_DELAY;
arrangeTimer.timeout.connect(() => {
    arrangeTimer.stop();
    arrangePending = false;
    arrange();
});

function scheduleArrange() {
    if (arrangePending) {
        return;
    }

    arrangePending = true;
    arrangeTimer.start();
}

function watchWindow(window) {
    if (!window || window.deleted) {
        return;
    }

    window.outputChanged.connect(scheduleArrange);
    window.desktopsChanged.connect(scheduleArrange);
    window.activitiesChanged.connect(scheduleArrange);
    window.minimizedChanged.connect(scheduleArrange);
    window.fullScreenChanged.connect(scheduleArrange);
    if (window.keepAboveChanged) {
        window.keepAboveChanged.connect(scheduleArrange);
    }
    if (window.keepBelowChanged) {
        window.keepBelowChanged.connect(scheduleArrange);
    }
}

function main() {
    workspace.windowList().forEach(watchWindow);
    workspace.windowAdded.connect((window) => {
        watchWindow(window);
        scheduleArrange();
    });
    workspace.windowRemoved.connect((window) => {
        managedWindows.delete(window);
        scheduleArrange();
    });
    workspace.currentDesktopChanged.connect(scheduleArrange);
    workspace.currentActivityChanged.connect(scheduleArrange);
    workspace.screensChanged.connect(scheduleArrange);
    workspace.virtualScreenGeometryChanged.connect(scheduleArrange);
    scheduleArrange();
}

main();
