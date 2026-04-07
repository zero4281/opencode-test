# Test Results: OmniCoder Qwen3.5 Custom (9B 112k)

## Test premise
Tested with: [OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF](https://ollama.com/zfujicute/OmniCoder-Qwen3.5-9B-Claude-4.6-Opus-Uncensored-v2-GGUF) with a 112k context window.  See my [blog post](https://joshrising.com/a-local-ai-coding-assistant-how-hard-could-it-be-pretty-hard-actually/) for additional details about the modelfile.

I changed the parameters to match some of the other tests to compare the results with the defaults.

```
PARAMETER temperature 0.6
PARAMETER top_k 20
PARAMETER top_p 0.95
PARAMETER min_p 0
PARAMETER num_ctx 114688
PARAMETER presence_penalty 0
PARAMETER repeat_penalty 1
PARAMETER stop <|im_start|>
PARAMETER stop <|im_end|>
PARAMETER stop <|endoftext|>
```

## Prompts that I had to run several times

Run \`python ./hf_search.py -q "Jackrong"\` and check it for errors.  Read the script.  Read the documentation.  Once the errors are identified, fixing them.  Here's the relevant documentation: https://huggingface.co/docs/huggingface_hub/en/package_reference/hf_api.md

Continue with the fix.