# Defined via `source`
function filter_opts --no-scope-shadowing
    set opts (string match  -- '-*' $argv)
    set args (string match --invert -- '-*' $argv)
end
