function city
    fd " $argv " -eJSON
    rg -S " $argv " --iglob '!*json'
end
