import os
from app.core.config import get_settings
from app.utils.prompt_utils import load_prompt

from openai import OpenAI
from groq import Groq

settings = get_settings()

def generate_markdown_summary(text: str, mode: str = "openai", model: str = None) -> str:
    prompt = load_prompt("summary_prompt.j2", {"body": text})

    if mode == "openai":
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        model = model or "gpt-4o-mini"
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "너는 한글 요약 전문가야."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2048, 
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    elif mode == "groq":
        client = Groq(api_key=settings.GROQ_API_KEY)
        model = model or "openai/gpt-oss-120b"
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "너는 한글 요약 전문가야."},
                {"role": "user", "content": prompt}
            ],
            model=model,
            max_tokens=2048,
            temperature=0.3,
        )
        return chat_completion.choices[0].message.content.strip()
    else:
        raise ValueError(f"Unknown mode: {mode}")

def generate_brief_summary(text: str, model: str = "gpt-4o-mini") -> str:
    prompt = load_prompt("brief_summary_prompt.j2", {"body": text})
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "너는 콘텐츠 큐레이션 전문가야."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=512,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()
