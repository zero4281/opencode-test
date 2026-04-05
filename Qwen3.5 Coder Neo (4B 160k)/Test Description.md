# Test Results: Qwen3.5 Coder Neo (4B 160k)

## Test premise
Tested with: [hf.co/Jackrong/Qwen3.5-4B-Neo-GGUF:Q5_K_M](https://huggingface.co/Jackrong/Qwen3.5-4B-Neo-GGUF) with a 160k context window.  See my [blog post](https://joshrising.com/a-local-ai-coding-assistant-how-hard-could-it-be-pretty-hard-actually/) for additional details about the modelfile.

## Prompts that I had to run several times

Run \`python ./hf_search.py -q "Jackrong"\` and check it for errors.  Once the errors are identified, fix them.  Here's some relevant documentation: https://huggingface.co/docs/huggingface_hub/en/package_reference/hf_api.md

Continue with the fix. (I had to run this like half a dozen times inbetween the previous fix prompt.  It must get stuck in a thinking block or something.)