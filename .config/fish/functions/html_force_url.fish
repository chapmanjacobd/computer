# Defined interactively
function html_force_url --argument-names url
    echo "<a style=\"color: rgb(57, 155, 226);\" href=\"$url#\" target=\"_blank\">$url</a>"
end
