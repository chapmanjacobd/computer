# Defined interactively
function search.flatpak

    for remote in (flatpak remotes --columns=name | grep -v Name)
        echo $remote
        sudo flatpak remote-ls $remote | grep -i $argv
    end
end
