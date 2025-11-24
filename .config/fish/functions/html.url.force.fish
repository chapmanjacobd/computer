# Defined interactively
function html.url.force --argument-names url
    echo "<a style=\"color: rgb(57, 155, 226);\" href=\"$url#\" target=\"_blank\">$url</a>"
end
