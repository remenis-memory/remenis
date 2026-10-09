import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from remenis.security.guard import RingContextGuard
from remenis.logging_config import setup_stream_logging

logger = setup_stream_logging()
limiter = Limiter(key_func=get_remote_address)
guard = RingContextGuard()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Remenis Live Stream Honeypot initialized.")
    logger.info("Monitoring memory space at /home/remenismemory/remenis")
    yield

app = FastAPI(title="Remenis Honeypot", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/challenge/prompt")
@limiter.limit("5/10second")
async def process_prompt(request: Request):
    body = await request.json()
    raw_prompt = body.get("prompt", "")
    logger.info(f"Incoming prompt: {raw_prompt}")
    
    sanitized_response = guard.sanitize_output(raw_prompt)
    logger.info(f"Processed response: {sanitized_response}")
    
    return {"status": "success", "response": sanitized_response}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
