# Defined interactively
function git.clone.selective
    git clone --filter=blob:none --sparse $argv[1] selective
    git -C selective sparse-checkout add $argv[2..-1]
end
