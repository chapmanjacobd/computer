# Defined in - @ line 2
function ip.public
    dig -4 +short myip.opendns.com @resolver1.opendns.com
end
