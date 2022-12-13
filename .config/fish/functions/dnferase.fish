# Defined interactively
function dnferase
for arg in $argv
filterfile ~/.github/dnf_installed $arg
end
sudo dnf erase $argv
end
