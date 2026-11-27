# Defined interactively
function phone.copy.func --wraps='cp'
    ~/phone/
    cp ~/.config/fish/functions/$argv.fish .config/fish/functions/
    wipp
end
