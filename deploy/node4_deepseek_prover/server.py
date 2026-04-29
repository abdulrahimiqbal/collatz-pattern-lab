import os
import threading
import time
from typing import Any, Dict, Optional

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig


MODEL_ID = os.getenv("MODEL_ID", "deepseek-ai/DeepSeek-Prover-V2-7B")
LOAD_IN_4BIT = os.getenv("LOAD_IN_4BIT", "1").lower() not in {"0", "false", "no"}
GPU_MAX_MEMORY = os.getenv("GPU_MAX_MEMORY", "11GiB")
CPU_MAX_MEMORY = os.getenv("CPU_MAX_MEMORY", "80GiB")
MAX_TOTAL_TOKENS = int(os.getenv("MAX_TOTAL_TOKENS", "8192"))
DEFAULT_MAX_NEW_TOKENS = int(os.getenv("DEFAULT_MAX_NEW_TOKENS", "1024"))
MAX_NEW_TOKENS_LIMIT = int(os.getenv("MAX_NEW_TOKENS_LIMIT", "4096"))

PROVER_PROMPT = """Complete the following Lean 4 code:

```lean4
{}
```
Before producing the Lean 4 code to formally prove the given theorem, provide a detailed proof plan outlining the main proof steps and strategies.
The plan should highlight key ideas, intermediate lemmas, and proof structures that will guide the construction of the final formal proof.""".strip()


class GenerateRequest(BaseModel):
    prompt: Optional[str] = Field(default=None, description="Raw user prompt.")
    formal_statement: Optional[str] = Field(
        default=None,
        description="Lean 4 statement containing a theorem with sorry. Uses the DeepSeek-Prover prompt template.",
    )
    max_new_tokens: int = Field(default=DEFAULT_MAX_NEW_TOKENS, ge=1, le=MAX_NEW_TOKENS_LIMIT)
    temperature: float = Field(default=0.6, ge=0.0, le=2.0)
    top_p: float = Field(default=0.95, ge=0.0, le=1.0)
    do_sample: bool = True
    seed: Optional[int] = None


class GenerateResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())

    text: str
    input_tokens: int
    output_tokens: int
    elapsed_seconds: float
    model_id: str
    quantization: str
    gpu: Dict[str, Any]


app = FastAPI(title="DeepSeek-Prover-V2-7B Node4 Service")
tokenizer: Any = None
model: Any = None
generate_lock = threading.Lock()
startup_error: Optional[str] = None


def _gpu_snapshot() -> Dict[str, Any]:
    if not torch.cuda.is_available():
        return {"cuda": False}
    device = torch.cuda.current_device()
    return {
        "cuda": True,
        "device": device,
        "name": torch.cuda.get_device_name(device),
        "allocated_mib": round(torch.cuda.memory_allocated(device) / 1024**2, 1),
        "reserved_mib": round(torch.cuda.memory_reserved(device) / 1024**2, 1),
    }


def _build_prompt(request: GenerateRequest) -> str:
    if request.formal_statement and request.prompt:
        raise HTTPException(status_code=400, detail="Use either formal_statement or prompt, not both.")
    if request.formal_statement:
        return PROVER_PROMPT.format(request.formal_statement.strip())
    if request.prompt:
        return request.prompt.strip()
    raise HTTPException(status_code=400, detail="Provide prompt or formal_statement.")


def _load_model() -> None:
    global tokenizer, model

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available; this service is intended for the RTX GPU on Node4.")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = None
    torch_dtype = torch.float16
    if LOAD_IN_4BIT:
        quantization_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.float16,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_use_double_quant=True,
        )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        trust_remote_code=True,
        torch_dtype=torch_dtype,
        low_cpu_mem_usage=True,
        device_map="auto",
        max_memory={0: GPU_MAX_MEMORY, "cpu": CPU_MAX_MEMORY},
        quantization_config=quantization_config,
    )
    model.eval()


@app.on_event("startup")
def startup() -> None:
    global startup_error
    try:
        _load_model()
    except Exception as exc:
        startup_error = repr(exc)
        raise


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "ok": model is not None and startup_error is None,
        "model_id": MODEL_ID,
        "quantization": "4bit-nf4" if LOAD_IN_4BIT else "none",
        "max_total_tokens": MAX_TOTAL_TOKENS,
        "max_new_tokens_limit": MAX_NEW_TOKENS_LIMIT,
        "startup_error": startup_error,
        "gpu": _gpu_snapshot(),
    }


@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest) -> GenerateResponse:
    if model is None or tokenizer is None:
        raise HTTPException(status_code=503, detail=f"Model is not loaded: {startup_error}")

    prompt = _build_prompt(request)
    if request.seed is not None:
        torch.manual_seed(request.seed)
        torch.cuda.manual_seed_all(request.seed)

    chat = [{"role": "user", "content": prompt}]
    inputs = tokenizer.apply_chat_template(
        chat,
        tokenize=True,
        add_generation_prompt=True,
        return_tensors="pt",
    )
    input_tokens = int(inputs.shape[-1])
    if input_tokens + request.max_new_tokens > MAX_TOTAL_TOKENS:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Requested {input_tokens + request.max_new_tokens} total tokens; "
                f"limit is {MAX_TOTAL_TOKENS} for the 12 GB RTX 3060 deployment."
            ),
        )

    inputs = inputs.to(model.device)
    generation_kwargs: Dict[str, Any] = {
        "max_new_tokens": request.max_new_tokens,
        "pad_token_id": tokenizer.pad_token_id,
        "eos_token_id": tokenizer.eos_token_id,
        "use_cache": True,
    }
    if request.do_sample:
        generation_kwargs.update(
            {
                "do_sample": True,
                "temperature": request.temperature,
                "top_p": request.top_p,
            }
        )
    else:
        generation_kwargs["do_sample"] = False

    start = time.time()
    with generate_lock, torch.inference_mode():
        outputs = model.generate(inputs, **generation_kwargs)
    elapsed = time.time() - start

    new_tokens = outputs[0, input_tokens:]
    text = tokenizer.decode(new_tokens, skip_special_tokens=True)
    return GenerateResponse(
        text=text,
        input_tokens=input_tokens,
        output_tokens=int(new_tokens.shape[-1]),
        elapsed_seconds=round(elapsed, 3),
        model_id=MODEL_ID,
        quantization="4bit-nf4" if LOAD_IN_4BIT else "none",
        gpu=_gpu_snapshot(),
    )
