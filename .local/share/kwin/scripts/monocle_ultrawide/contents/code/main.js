"use strict";

const OUTPUT_NAME = "dp-1";
const SIDE_GAP = 700;
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

    return window.dialog || window.splash || window.utility ||
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

function arrange() {
    for (const window of workspace.windowList()) {
        if (!isManaged(window)) {
            continue;
        }

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

function watchWindow(window) {
    if (!window || window.deleted) {
        return;
    }

    window.outputChanged.connect(arrange);
    window.desktopsChanged.connect(arrange);
    window.activitiesChanged.connect(arrange);
    window.minimizedChanged.connect(arrange);
    window.fullScreenChanged.connect(arrange);
}

function main() {
    workspace.windowList().forEach(watchWindow);
    workspace.windowAdded.connect((window) => {
        watchWindow(window);
        arrange();
    });
    workspace.windowRemoved.connect(arrange);
    workspace.currentDesktopChanged.connect(arrange);
    workspace.currentActivityChanged.connect(arrange);
    workspace.screensChanged.connect(arrange);
    workspace.virtualScreenGeometryChanged.connect(arrange);
    arrange();
}

main();
