"use strict";

const OUTPUT_NAME = "dp-1";
const SIDE_GAP = 700;
const ARRANGE_DELAY = 50;
const EDGE_ZONE = 70;
const GRID_LEFT = 0;
const GRID_CENTER_TOP = 1;
const GRID_CENTER_BOTTOM = 2;
const GRID_RIGHT = 3;
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

    return window.keepAbove ||
        window.skipTaskbar || window.skipPager ||
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
const initializedWindows = new Set();
const manualSlots = new Map();
const activeMoves = new Set();

function initializeWindow(window) {
    if (!window || initializedWindows.has(window) ||
        !window.output || window.minimized || !window.normalWindow) {
        return;
    }

    initializedWindows.add(window);
    window.keepAbove = false;
    window.keepBelow = false;
    if (isIgnored(window)) {
        return;
    }

    if (text(window.output.name) === OUTPUT_NAME ||
        !window.maximizable || window.maximizeMode > 0) {
        return;
    }

    window.setMaximize(true, true);
}

function getLayoutArea(area) {
    return {
        x: area.x + SIDE_GAP,
        y: area.y,
        width: area.width - SIDE_GAP * 2,
        height: area.height,
    };
}

// Drop zones (by cursor position): the side gaps are the left/right slots;
// in the center column, dropping near the top/bottom screen edge picks that
// half; anywhere else is monocle.
function getDropSlot(point, area) {
    const layout = getLayoutArea(area);
    if (point.x < layout.x) {
        return GRID_LEFT;
    }
    if (point.x >= layout.x + layout.width) {
        return GRID_RIGHT;
    }
    if (point.y < layout.y + EDGE_ZONE) {
        return GRID_CENTER_TOP;
    }
    if (point.y >= layout.y + layout.height - EDGE_ZONE) {
        return GRID_CENTER_BOTTOM;
    }
    return undefined;
}

function getGridGeometry(area, slot) {
    const layout = getLayoutArea(area);
    const centerHeight = Math.floor(layout.height / 2);

    switch (slot) {
        case GRID_LEFT:
            return { x: area.x, y: area.y, width: SIDE_GAP, height: area.height };
        case GRID_CENTER_TOP:
            return { x: layout.x, y: layout.y, width: layout.width, height: centerHeight };
        case GRID_CENTER_BOTTOM:
            return {
                x: layout.x,
                y: layout.y + centerHeight,
                width: layout.width,
                height: layout.height - centerHeight,
            };
        case GRID_RIGHT:
            return {
                x: layout.x + layout.width,
                y: area.y,
                width: area.x + area.width - layout.x - layout.width,
                height: area.height,
            };
    }
}

function updateManualSlot(window, wasResize) {
    if (!isManaged(window)) {
        manualSlots.delete(window);
        scheduleArrange();
        return;
    }
    if (wasResize) {
        scheduleArrange();
        return;
    }

    const area = workspace.clientArea(KWin.MaximizeArea, window);
    const slot = getDropSlot(workspace.cursorPos, area);
    if (slot === undefined) {
        manualSlots.delete(window);
        scheduleArrange();
        return;
    }

    for (const [otherWindow, otherSlot] of manualSlots) {
        if (otherWindow === window || otherSlot === slot) {
            manualSlots.delete(otherWindow);
        }
    }
    manualSlots.set(window, slot);
    scheduleArrange();
}

function arrange() {
    for (const window of workspace.windowList()) {
        if (activeMoves.has(window)) {
            continue;
        }

        initializeWindow(window);

        if (!isManaged(window)) {
            if (!managedWindows.has(window)) {
                continue;
            }

            if (!window.output || text(window.output.name) === OUTPUT_NAME) {
                if (isIgnored(window)) {
                    manualSlots.delete(window);
                    managedWindows.delete(window);
                }
                continue;
            }

            if (!isIgnored(window) && window.maximizable && !window.fullScreen) {
                window.setMaximize(true, true);
            }
            manualSlots.delete(window);
            managedWindows.delete(window);
            continue;
        }

        managedWindows.add(window);

        if (window.maximizeMode > 0) {
            window.setMaximize(false, false);
        }

        if (window.tile) {
            window.tile = null;
        }

        const geometry = workspace.clientArea(KWin.MaximizeArea, window);
        const manualSlot = manualSlots.get(window);
        if (manualSlot !== undefined) {
            window.frameGeometry = getGridGeometry(geometry, manualSlot);
            continue;
        }

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
    if (window.skipTaskbarChanged) {
        window.skipTaskbarChanged.connect(scheduleArrange);
    }
    if (window.skipPagerChanged) {
        window.skipPagerChanged.connect(scheduleArrange);
    }
    let wasResize = false;
    window.interactiveMoveResizeStarted.connect(() => {
        wasResize = !!window.resize;
        activeMoves.add(window);
    });
    window.interactiveMoveResizeFinished.connect(() => {
        activeMoves.delete(window);
        updateManualSlot(window, wasResize);
    });
}

function main() {
    workspace.windowList().forEach(watchWindow);
    workspace.windowAdded.connect((window) => {
        watchWindow(window);
        scheduleArrange();
    });
    workspace.windowRemoved.connect((window) => {
        activeMoves.delete(window);
        initializedWindows.delete(window);
        manualSlots.delete(window);
        managedWindows.delete(window);
        scheduleArrange();
    });
    workspace.currentDesktopChanged.connect(scheduleArrange);
    workspace.currentActivityChanged.connect(scheduleArrange);
    workspace.screensChanged.connect(scheduleArrange);
    workspace.virtualScreenGeometryChanged.connect(scheduleArrange);
    if (workspace.clientAreaChanged) {
        workspace.clientAreaChanged.connect(scheduleArrange);
    }
    scheduleArrange();
}

main();
