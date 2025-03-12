curl -X POST "http://localhost:11434/api/generate" \
-H "Content-Type: application/json" \
-d '{"model": "qwen2.5:14b", "prompt": "This is a test prompt.", "max_tokens": 50}'