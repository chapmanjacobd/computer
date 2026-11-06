"use strict";

const OUTPUT_NAME = "dp-1";
const SIDE_GAP = 700;
const ARRANGE_DELAY = 50;
const EDGE_SNAP_TOLERANCE = 32;
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

    return window.keepAbove || window.keepBelow ||
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
const manualSlots = new Map();
const activeMoves = new Set();

function isEdgeSnapped(geometry, area) {
    return Math.abs(geometry.x - area.x) <= EDGE_SNAP_TOLERANCE ||
        Math.abs(geometry.x + geometry.width - area.x - area.width) <= EDGE_SNAP_TOLERANCE ||
        Math.abs(geometry.y - area.y) <= EDGE_SNAP_TOLERANCE ||
        Math.abs(geometry.y + geometry.height - area.y - area.height) <= EDGE_SNAP_TOLERANCE;
}

function getManualSlot(geometry, area) {
    const centerX = geometry.x + geometry.width / 2;
    const centerY = geometry.y + geometry.height / 2;

    if (centerX <= area.x + area.width / 3) {
        return GRID_LEFT;
    }
    if (centerX >= area.x + area.width * 2 / 3) {
        return GRID_RIGHT;
    }
    return centerY <= area.y + area.height / 2
        ? GRID_CENTER_TOP
        : GRID_CENTER_BOTTOM;
}

function getGridGeometry(area, slot) {
    const x = area.x + SIDE_GAP;
    const width = area.width - SIDE_GAP * 2;
    const leftWidth = Math.floor(width / 4);
    const centerWidth = Math.floor(width / 2);
    const rightWidth = width - leftWidth - centerWidth;
    const centerX = x + leftWidth;
    const rightX = centerX + centerWidth;
    const centerHeight = Math.floor(area.height / 2);

    switch (slot) {
        case GRID_LEFT:
            return { x: x, y: area.y, width: leftWidth, height: area.height };
        case GRID_CENTER_TOP:
            return { x: centerX, y: area.y, width: centerWidth, height: centerHeight };
        case GRID_CENTER_BOTTOM:
            return {
                x: centerX,
                y: area.y + centerHeight,
                width: centerWidth,
                height: area.height - centerHeight,
            };
        case GRID_RIGHT:
            return { x: rightX, y: area.y, width: rightWidth, height: area.height };
    }
}

function updateManualSlot(window) {
    if (!isManaged(window)) {
        manualSlots.delete(window);
        scheduleArrange();
        return;
    }

    const area = workspace.clientArea(KWin.FullArea, window);
    const geometry = window.frameGeometry;
    if (!isEdgeSnapped(geometry, area)) {
        manualSlots.delete(window);
        scheduleArrange();
        return;
    }

    const slot = getManualSlot(geometry, area);
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

        const geometry = workspace.clientArea(KWin.FullArea, window);
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
    if (window.moveResizedChanged) {
        let wasMoving = false;
        window.moveResizedChanged.connect(() => {
            const isMoving = window.move || window.resize;
            if (isMoving) {
                wasMoving = true;
                activeMoves.add(window);
                return;
            }
            if (!wasMoving) {
                return;
            }
            wasMoving = false;
            activeMoves.delete(window);
            updateManualSlot(window);
        });
    }
}

function main() {
    workspace.windowList().forEach(watchWindow);
    workspace.windowAdded.connect((window) => {
        watchWindow(window);
        scheduleArrange();
    });
    workspace.windowRemoved.connect((window) => {
        activeMoves.delete(window);
        manualSlots.delete(window);
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
