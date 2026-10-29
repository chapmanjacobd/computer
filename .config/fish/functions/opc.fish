# Defined interactively
function opc --description 'OpenCode mini in monochrome (for low-bandwidth SSH session)'
    env OPENCODE_CLI_CONFIG_CONTENT='{"mini":{"mono":true}}' opencode mini --no-replay $argv
end
