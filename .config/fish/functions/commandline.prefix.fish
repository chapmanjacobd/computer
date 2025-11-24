# Defined interactively
function commandline.prefix
    if not set -q COMMAND_PREFIX
        # --- ACTIVATE ---
        if test -z "$argv[1]"
            echo "Commandline prefix not active" >&2
            return 1
        end

        bind \r _exec_with_prefix
        bind \n _exec_with_prefix

        set -g COMMAND_PREFIX $argv
    else # --- DEACTIVATE ---
        bind \r execute
        bind \n execute

        set -e COMMAND_PREFIX
    end
end
