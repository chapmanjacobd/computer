function chars.no.trailingslash
    read str
    string replace -r '/$' '' $str
end
