# Defined via `source`
function forganize_d03
    ~/d/03_Downloads/ && fd -eZIP -eRAR -e7z -x bash -c 'unar "{}" && rm "{}"'

    ~/d/03_Downloads/ && fd -d1 -eEPUB -x mv "{}" ~/d/50_eBooks/
    ~/d/03_Downloads/ && fd -d1 -eHTML -x mv "{}" ~/d/53_Scrapbook_Web/

    ~/d/03_Downloads/ && fd -d1 -eJPEG -x mv "{}" {.}.jpg
    ~/d/03_Downloads/ && fd -d1 -eJPG -ePNG -eWEBP -x mv "{}" ~/d/61_Photos_Unsorted/
end
