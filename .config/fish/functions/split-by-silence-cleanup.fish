# Defined interactively
function split-by-silence-cleanup
    fd .000. | grep -i '\.000\.' | sed 's|\.000\..*||' | string escape | xargs trash
end
