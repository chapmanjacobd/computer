# Defined via `source`
function llm_pytest
    llm -p "<|im_start|>system
You are an expert python programmer. Return a pytest function without repeating the existing code.<|im_end|>
<|im_start|>$(cb)<|im_end|>
<|im_start|>assistant
"
end
