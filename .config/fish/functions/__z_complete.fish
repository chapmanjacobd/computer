function __z_complete
    set -l tokens (commandline --current-process --tokenize)
    set -l curr_tokens (commandline --cut-at-cursor --current-process --tokenize)

    set -l query $tokens[2..-1]
    set -l result (zoxide query --exclude (__zoxide_pwd) --interactive -- $query)
    and echo $__zoxide_z_prefix$result
    commandline --function repaint
end

complete --command z --no-files --arguments '(__z_complete)'
