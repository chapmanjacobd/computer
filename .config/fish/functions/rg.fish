# Defined interactively
function rg
    command rg -i --no-heading --no-line-number -. --no-ignore-files $argv
end
