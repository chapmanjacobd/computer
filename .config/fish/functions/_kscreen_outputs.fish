function _kscreen_outputs
    kscreen-doctor -o 2>&1 |
        sed -E 's/\x1B\[[0-9;]*m//g' |
        string match -r '^Output: [0-9]+ [^ ]+' |
        string replace -r '^Output: [0-9]+ ' ''
end
