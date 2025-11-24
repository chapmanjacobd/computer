# Defined via `source`
function optparse --no-scope-shadowing
    set opts (string match  -- '-*' $argv)
    set args (string match --invert -- '-*' $argv)
end
