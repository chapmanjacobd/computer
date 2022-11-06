# Defined interactively
function trash-split-by-silence-records
    fd .000. | grep -i '\.000\.' | sed 's|\.000\..*||' | string escape | xargs trash-put
end
