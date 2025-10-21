# api/openai_client.py
import os
import backoff
from typing import Optional
from openai import OpenAI

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client (adjust to the client library you use)
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else OpenAI()

def _normalize_model(model: str) -> str:
    # choose a default; replace with your preferred model
    return model or "gpt-4o-mini"

@backoff.on_exception(backoff.expo, Exception, max_tries=3)
def call_openai_chat(system_message: str, user_message: str, model: str = "gpt-4o-mini", temperature: float = 0.8, max_tokens: int = 1200) -> str:
    model = _normalize_model(model)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ],
        temperature=temperature,
        max_tokens=max_tokens
    )
    # return the model text
    return resp.choices[0].message.content
