from fastapi import FastAPI, Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from remenis.security.guard import RingContextGuard

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Remenis Ring Isolation Honeypot API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

guard = RingContextGuard()

@app.post("/api/v1/challenge/prompt")
@limiter.limit("5/10seconds")
@limiter.limit("30/hour")
async def submit_challenge_prompt(request: Request, payload: dict):
    user_prompt = payload.get("prompt", "").strip()

    if not user_prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty.")

    if len(user_prompt) > 1000:
        raise HTTPException(status_code=400, detail="Prompt exceeds 1000 character limit.")

    isolated_env = guard.get_isolated_env()
    agent_raw_response = f"Processed prompt safely: '{user_prompt}'"

    sanitized_response = guard.sanitize_output(agent_raw_response)

    return {
        "status": "success",
        "ring_isolation": "active",
        "response": sanitized_response
    }
