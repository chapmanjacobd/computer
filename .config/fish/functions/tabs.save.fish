# Defined interactively
function tabs.save
    cb >>~/mc/tabs
    for url in (cb)
        waybackpy -s --archive-url --url $url | grep http >>~/mc/tabs
    end
end
