"use strict";

const INITIAL_WIDTH = 600;
const INITIAL_HEIGHT = 500;
const INITIAL_GEOMETRY_DELAY_MS = 200;

const placedInitially = new Set();

function isMpv(window) {
    return window &&
        !window.deleted &&
        window.normalWindow &&
        String(window.resourceClass).toLowerCase() === "mpv" &&
        String(window.resourceName).toLowerCase() === "mpv";
}

// Fullscreen mpv: visible in the taskbar and Alt+Tab, and not kept above
// other windows (KWin only uses the active-fullscreen layer while focused).
// Windowed mpv: hidden from both lists and kept above other windows.
function syncWindowState(window) {
    if (!isMpv(window) || window.deleted) {
        return;
    }

    const skipWindowLists = !window.fullScreen;

    if (window.skipTaskbar !== skipWindowLists) {
        window.skipTaskbar = skipWindowLists;
    }
    if (window.skipSwitcher !== skipWindowLists) {
        window.skipSwitcher = skipWindowLists;
    }
    if (window.keepAbove !== !window.fullScreen) {
        window.keepAbove = !window.fullScreen;
    }
}

function placeInitialGeometry(window) {
    if (!isMpv(window) || window.deleted || window.fullScreen ||
        placedInitially.has(window)) {
        return;
    }
    placedInitially.add(window);

    // MaximizeArea is the window's output minus panels/taskbars.
    const area = workspace.clientArea(KWin.MaximizeArea, window);
    const width = Math.min(INITIAL_WIDTH, area.width);
    const height = Math.min(INITIAL_HEIGHT, area.height);

    window.frameGeometry = {
        x: Math.round(area.x + area.width - width),
        y: Math.round(area.y + area.height - height),
        width: Math.round(width),
        height: Math.round(height),
    };
}

function setupWindow(window) {
    if (!isMpv(window)) {
        return;
    }

    syncWindowState(window);

    window.fullScreenChanged.connect(() => {
        syncWindowState(window);
        // If mpv started fullscreen, give it the intended windowed geometry
        // the first time it leaves fullscreen.
        placeInitialGeometry(window);
    });
    window.skipTaskbarChanged.connect(() => syncWindowState(window));
    window.skipSwitcherChanged.connect(() => syncWindowState(window));
    window.keepAboveChanged.connect(() => syncWindowState(window));

    // mpv commits its own initial size after the window is added. Apply the
    // placement once after that, then stop managing the geometry so manual
    // moves and resizes are preserved.
    const timer = new QTimer();
    timer.singleShot = true;
    timer.interval = INITIAL_GEOMETRY_DELAY_MS;
    timer.timeout.connect(() => {
        placeInitialGeometry(window);
        syncWindowState(window);
    });
    timer.start();
    window._mpvBehaviorTimer = timer;
}

workspace.windowList().forEach(setupWindow);
workspace.windowAdded.connect(setupWindow);
workspace.windowRemoved.connect((window) => {
    placedInitially.delete(window);
});
