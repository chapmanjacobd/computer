# Defined via `source`
function javtiful_links --argument query total
    set last_page (math -s 0 "1+($total/23)")
    echo 'https://javtiful.com/'$query'&page='(seq 1 $last_page) | string split ' ' | parallel lb links {} --include /video/ | tee /dev/tty >>~/.jobs/javtiful_misc
end
