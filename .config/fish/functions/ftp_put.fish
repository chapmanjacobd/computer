# Defined interactively
function ftp_put
    curl -T "$argv" ftp://192.168.1.119:5000 --globoff -k
end
