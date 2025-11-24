# Defined via `source`
function llm.python
    llm -p "<|im_start|>system
You are an expert python programmer. Return a python implementation without repeating the existing code.<|im_end|>
<|im_start|>$(cb)<|im_end|>
<|im_start|>assistant
"
end
