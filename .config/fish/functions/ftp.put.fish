# Defined interactively
function ftp.put --wraps='curl'
    curl -T "$argv" ftp://192.168.1.119:5000 --globoff -k
end
