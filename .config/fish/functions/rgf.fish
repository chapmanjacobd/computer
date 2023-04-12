# Defined interactively
function rgf
    less -FSRXc (rg -i --no-heading --no-line-number --files-with-matches -j1 $argv)
end
