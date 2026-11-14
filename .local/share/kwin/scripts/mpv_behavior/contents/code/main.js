"use strict";

const PLACEMENT_INTERVAL_MS = 50;
const PLACEMENT_ATTEMPTS = 6;
const ACTIVE_HISTORY_LIMIT = 8;

const placedInitially = new Set();
const placementScheduled = new Set();
const stackPlacementHandled = new Set();
const newWindows = new Set();
const activeHistory = [];
const constrainedBelow = new Map();

function isMpv(window) {
    return window &&
        !window.deleted &&
        window.normalWindow &&
        String(window.resourceClass).toLowerCase() === "mpv" &&
        String(window.resourceName).toLowerCase() === "mpv";
}

function isFullscreenMpv(window) {
    return isMpv(window) && window.fullScreen;
}

function sameOutput(a, b) {
    return !a.output || !b.output || a.output === b.output;
}

function rememberActive(window) {
    if (!window || window.deleted || !window.normalWindow) {
        return;
    }

    const index = activeHistory.indexOf(window);
    if (index !== -1) {
        activeHistory.splice(index, 1);
    }
    activeHistory.push(window);
    if (activeHistory.length > ACTIVE_HISTORY_LIMIT) {
        activeHistory.shift();
    }
}

function previousActiveWindow(exclude) {
    for (let i = activeHistory.length - 1; i >= 0; i--) {
        const candidate = activeHistory[i];
        if (candidate !== exclude && !candidate.deleted && candidate.normalWindow) {
            return candidate;
        }
    }
    return null;
}

function addConstraint(below, above) {
    if (below === above || typeof workspace.constrain !== "function") {
        return;
    }

    let aboveWindows = constrainedBelow.get(below);
    if (!aboveWindows) {
        aboveWindows = new Set();
        constrainedBelow.set(below, aboveWindows);
    }
    if (aboveWindows.has(above)) {
        return;
    }

    aboveWindows.add(above);
    workspace.constrain(below, above);
}

function releaseConstraints(below) {
    const aboveWindows = constrainedBelow.get(below);
    if (!aboveWindows) {
        return;
    }

    if (typeof workspace.unconstrain === "function") {
        for (const above of aboveWindows) {
            if (!above.deleted) {
                workspace.unconstrain(below, above);
            }
        }
    }
    constrainedBelow.delete(below);
}

// On Wayland, KWin activates new windows more aggressively than on X11, so a
// new fullscreen mpv window would cover the video that is already on screen.
// Constrain it under the existing fullscreen mpv windows and give focus back
// to whatever was active before. When the user activates it, the constraints
// are released so it can be raised normally.
function keepNewWindowBehindStack(window) {
    if (!newWindows.has(window) || !isFullscreenMpv(window) || stackPlacementHandled.has(window)) {
        return;
    }
    stackPlacementHandled.add(window);

    const existing = [];
    for (const other of workspace.windowList()) {
        if (other !== window && other.onCurrentDesktop && isFullscreenMpv(other) && sameOutput(other, window)) {
            existing.push(other);
        }
    }

    // The first window of a stack should behave normally.
    if (existing.length === 0) {
        return;
    }

    for (const other of existing) {
        addConstraint(window, other);
    }

    if (workspace.activeWindow === window) {
        const previousActive = previousActiveWindow(window);
        if (previousActive) {
            workspace.activeWindow = previousActive;
        }
    }
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

function setupWindow(window, newlyAdded) {
    if (!isMpv(window)) {
        return;
    }
    if (newlyAdded) {
        newWindows.add(window);
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
        if (window.fullScreen) {
            keepNewWindowBehindStack(window);
        }
    });
    window.skipTaskbarChanged.connect(() => syncWindowState(window));
    window.skipSwitcherChanged.connect(() => syncWindowState(window));
    window.keepAboveChanged.connect(() => syncWindowState(window));

    // mpv commits its own initial size after the window is added. Retry the
    // placement for a short period so late size changes and KWin's restore
    // after unmaximizing are handled.
    placeBottomRight(window);
    if (window.fullScreen) {
        keepNewWindowBehindStack(window);
    }
}

rememberActive(workspace.activeWindow);

workspace.windowList().forEach((window) => setupWindow(window, false));
workspace.windowAdded.connect((window) => setupWindow(window, true));
workspace.windowActivated.connect((window) => {
    rememberActive(window);
    // The user picked this window; let it rise above the stack it was kept under.
    releaseConstraints(window);
});
workspace.windowRemoved.connect((window) => {
    placedInitially.delete(window);
    placementScheduled.delete(window);
    stackPlacementHandled.delete(window);
    newWindows.delete(window);
    const activeIndex = activeHistory.indexOf(window);
    if (activeIndex !== -1) {
        activeHistory.splice(activeIndex, 1);
    }
    releaseConstraints(window);

    for (const [below, aboveWindows] of constrainedBelow) {
        aboveWindows.delete(window);
        if (aboveWindows.size === 0) {
            constrainedBelow.delete(below);
        }
    }
});
