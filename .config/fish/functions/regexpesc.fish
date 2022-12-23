function regexpesc
    echo $argv | string escape --style=regex | string replace / '\/' -a | string replace -a '&' '\&' | xclip -selection c
end
