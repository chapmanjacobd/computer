# Defined interactively
function opc --description 'OpenCode mini in monochrome (for low-bandwidth SSH session)'
    set -l args (string escape -- $argv)
    if test (count $args) -eq 0
        set args -c
    end
    env OPENCODE_CLI_CONFIG_CONTENT='{"mini":{"mono":true}}' opencode mini --no-replay $args
end
