# Defined interactively
function search.text.paths
    less -FSRXc (rg -i --no-heading --no-line-number --files-with-matches -j1 $argv)
end
