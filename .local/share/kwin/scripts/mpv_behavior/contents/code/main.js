"use strict";

const INITIAL_PLACEMENT_DELAY_MS = 250;

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

function moveBottomRight(window) {
    if (!isMpv(window) || window.deleted || window.fullScreen) {
        return;
    }

    // Keep mpv's aspect-correct size (autofit/geometry); only move the
    // window to the bottom-right of its output's work area.
    const area = workspace.clientArea(KWin.MaximizeArea, window);
    const size = window.frameGeometry;
    window.frameGeometry = {
        x: Math.round(area.x + area.width - size.width),
        y: Math.round(area.y + area.height - size.height),
        width: size.width,
        height: size.height,
    };
}

function placeBottomRight(window) {
    if (!isMpv(window) || window.deleted || window.fullScreen ||
        placedInitially.has(window)) {
        return;
    }
    placedInitially.add(window);

    // KWin's "Maximizing" placement policy can leave mpv marked as maximized
    // even when its actual size is small. Clear that state first, then move
    // it after KWin has restored its pre-maximized geometry.
    if (window.maximizeMode !== 0) {
        window.setMaximize(false, false);
        const timer = new QTimer();
        timer.singleShot = true;
        timer.interval = 100;
        timer.timeout.connect(() => moveBottomRight(window));
        timer.start();
        window._mpvPlacementTimer = timer;
        return;
    }

    moveBottomRight(window);
}

function setupWindow(window) {
    if (!isMpv(window)) {
        return;
    }

    syncWindowState(window);

    // KWin's "Maximizing" placement policy marks new windows as maximized.
    // Clear that immediately while mpv is still windowed; leaving it set can
    // make mpv restore to a full-screen-sized window after fullscreen.
    if (!window.fullScreen && window.maximizeMode !== 0) {
        window.setMaximize(false, false);
    }

    window.fullScreenChanged.connect(() => {
        syncWindowState(window);
        // If mpv started fullscreen, place it bottom-right the first time it
        // leaves fullscreen.
        placeBottomRight(window);
    });
    window.skipTaskbarChanged.connect(() => syncWindowState(window));
    window.skipSwitcherChanged.connect(() => syncWindowState(window));
    window.keepAboveChanged.connect(() => syncWindowState(window));

    // mpv commits its own initial size after the window is added. Move it
    // once after that, then stop managing the geometry so manual moves and
    // resizes are preserved.
    const timer = new QTimer();
    timer.singleShot = true;
    timer.interval = INITIAL_PLACEMENT_DELAY_MS;
    timer.timeout.connect(() => {
        placeBottomRight(window);
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
