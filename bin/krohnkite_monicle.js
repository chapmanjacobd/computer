function toggleGlobalGaps() {
  if (workspace.globalGapsEnabled === undefined) {
    workspace.globalGapsEnabled = false;
  }

  workspace.globalGapsEnabled = !workspace.globalGapsEnabled;

  const gapWidth = 768;

  const screens = workspace.screens;
  for (let s = 0; s < screens; ++s) {
    const screen = screens[s];
    const screenGeometry = workspace.screenGeometry(screen);
    const screenWidth = screenGeometry.width;
    const screenHeight = screenGeometry.height;

    const windows = workspace.clientList();
    for (let i = 0; i < windows.length; ++i) {
      const client = windows[i];
      if (client.screen !== screen) continue; // Skip windows on other screens

      if (workspace.globalGapsEnabled) {
        client.geometry = {
          x: gapWidth,
          y: 0,
          width: screenWidth - 2 * gapWidth,
          height: screenHeight,
        };
      } else {
        client.geometry = {
          x: 0,
          y: 0,
          width: screenWidth,
          height: screenHeight,
        };
      }
    }
  }
}

workspace.clientAdded.connect(function(client) {
  if (workspace.globalGapsEnabled) {
    const gapWidth = 768;

    const screenGeometry = workspace.screenGeometry(client.screen);
    const screenWidth = screenGeometry.width;
    const screenHeight = screenGeometry.height;

    client.geometry = {
      x: gapWidth,
      y: 0,
      width: screenWidth - 2 * gapWidth,
      height: screenHeight,
    };
  }
});
