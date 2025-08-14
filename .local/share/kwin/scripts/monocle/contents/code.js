// Define the buffer size in pixels for the left and right sides.
const BUFFER_SIZE = 700;

// The function that performs the core logic of resizing the window.
function applyMonocleLayout(client) {
  // Check if a client (window) exists and is not fullscreen.
  // We only want to tile normal, non-fullscreen windows.
  if (client && !client.fullScreen && client.resizeable) {
    // Get the geometry of the current screen.
    // The geometry provides the screen's x, y, width, and height.
    const screen = workspace.screenGeometry(workspace.currentScreen);

    // Calculate the new width for the window, subtracting the left and right buffers.
    const newWidth = screen.width - (BUFFER_SIZE * 2);

    // Set the new x position to be the left buffer size.
    const newX = BUFFER_SIZE;

    // Set the new geometry for the window.
    client.geometry = {
      x: newX,
      y: screen.y, // Keep the window at the top of the screen
      width: newWidth,
      height: screen.height // Make the window fill the full screen height
    };
  }
}

// Listen for when a new window becomes active (gets focus).
workspace.clientActivated.connect(applyMonocleLayout);

// Listen for when a new window is added.
// This ensures that even on launch, a window is immediately tiled.
workspace.clientAdded.connect(applyMonocleLayout);

// To ensure the layout is applied when the script starts (e.g., on login),
// we apply the layout to the currently active window.
if (workspace.activeClient) {
  applyMonocleLayout(workspace.activeClient);
}

// Additionally, we can connect to client geometry change to re-apply layout
// when a window is resized, but this might cause a loop if not handled carefully.
// A simpler approach is to connect to screen resize events.
workspace.screenResized.connect(function() {
  if (workspace.activeClient) {
    applyMonocleLayout(workspace.activeClient);
  }
});

