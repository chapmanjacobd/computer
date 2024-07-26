# Defined interactively
function ftp_put
    curl -T "$argv" ftp://192.168.68.56:5000 --globoff -k
end
