# Defined via `source`
function dorganize
    ~/d/03_Downloads/

    fd -eZIP -eRAR -e7z -x bash -c 'unar "{}" && rm "{}"'

    fd -d1 -eEPUB -edjvu -x mv "{}" ~/d/50_eBooks/
    fd -d1 -eHTML -ePDF -x mv "{}" ~/d/53_Scrapbook_Web/

    fd -d1 -eJPEG -x mv "{}" {.}.jpg
    fd -d1 -eJPG -ePNG -eWEBP -x mv "{}" ~/d/61_Photos_Unsorted/

    remove_empty_directories
    ls
end
