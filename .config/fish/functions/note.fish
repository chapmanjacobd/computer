function note
    if [ "$argv" != '' ]
        echo $argv >>~/notes.org
    else
        xclip -o -sel clip >>~/notes.org
        echo >>~/notes.org
    end
end
