# Defined interactively
function dl.ia.collection
    for s in $argv
        mkdir "$s"
        ia search "collection:$s" --itemlist | parallel --eta -j6 --timeout 800s ia download --source original {} --checksum --destdir "./$s"
    end
end
