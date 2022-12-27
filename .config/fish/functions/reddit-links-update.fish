function reddit-links-update --argument folder
    set curatifile "/home/xk/mc/""$folder""-reddit.txt"
    set subr (cat $curatifile | string join ', ')
    reddit-links-m "$subr" | grep '^http' >>~/.jobs/todo/$folder
end
