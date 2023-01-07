# Defined interactively
function pulumi-cp-secret --argument stack_from stack_to secret
    pulumi config set --secret -s $stack_to $secret (pulumi config get -s $stack_from $secret)
end
