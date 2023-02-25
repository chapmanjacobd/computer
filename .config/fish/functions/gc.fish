# Defined in - @ line 2
function gc
    git config --global --unset-all url.git@github.com:.insteadof
    git clone --depth=1 $argv
    git config --global url."git@github.com:".insteadOf https://github.com/
end
