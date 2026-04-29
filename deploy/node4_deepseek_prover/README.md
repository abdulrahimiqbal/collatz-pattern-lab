# DeepSeek-Prover-V2-7B Node4 Service

Small FastAPI deployment for `deepseek-ai/DeepSeek-Prover-V2-7B` on Node4's RTX 3060.

The service loads the model with 4-bit NF4 quantization because the upstream BF16 weights exceed 12 GB VRAM before KV cache.

## Remote Install

```bash
cd ~/deepseek-prover-v2-service
./install_env.sh
./start.sh
./status.sh
```

## API

```bash
curl http://127.0.0.1:8000/health
curl -X POST http://127.0.0.1:8000/generate \
  -H 'Content-Type: application/json' \
  --data @sample_request.json
```

Use `formal_statement` for Lean theorem completion with the DeepSeek-Prover prompt template, or `prompt` for a raw chat prompt.
