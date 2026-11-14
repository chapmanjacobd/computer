"use strict";

const PLACEMENT_INTERVAL_MS = 50;
const PLACEMENT_ATTEMPTS = 6;

const placedInitially = new Set();
const placementScheduled = new Set();

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

function attemptPlacement(window) {
    if (!isMpv(window) || window.deleted || window.fullScreen) {
        // If mpv entered fullscreen while this placement loop was running,
        // forget the placement so the unfullscreen handler runs it again.
        if (window && window.fullScreen) {
            placedInitially.delete(window);
        }
        return false;
    }

    // KWin's "Maximizing" placement policy can leave mpv marked as maximized
    // even when its actual size is small. Clear that state first; a later
    // attempt in the loop moves the window after KWin restores its size.
    if (window.maximizeMode !== 0) {
        window.setMaximize(false, false);
        return false;
    }

    moveBottomRight(window);
    placedInitially.add(window);
    return true;
}

function placeBottomRight(window) {
    if (!isMpv(window) || window.deleted || window.fullScreen ||
        placedInitially.has(window) || placementScheduled.has(window)) {
        return;
    }
    placementScheduled.add(window);

    let attempts = 0;
    const timer = new QTimer();
    timer.interval = PLACEMENT_INTERVAL_MS;
    timer.timeout.connect(() => {
        attempts++;
        attemptPlacement(window);

        if (attempts >= PLACEMENT_ATTEMPTS) {
            timer.stop();
            placementScheduled.delete(window);
        }
    });
    timer.start();
    window._mpvPlacementTimer = timer;
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

    // mpv commits its own initial size after the window is added. Retry the
    // placement for a short period so late size changes and KWin's restore
    // after unmaximizing are handled.
    placeBottomRight(window);
}

workspace.windowList().forEach(setupWindow);
workspace.windowAdded.connect(setupWindow);
workspace.windowRemoved.connect((window) => {
    placedInitially.delete(window);
    placementScheduled.delete(window);
});
