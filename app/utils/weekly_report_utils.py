from app.core.config import get_settings
from app.utils.prompt_utils import load_prompt
from openai import OpenAI

settings = get_settings()

def generate_weekly_insight_report_markdown(
    brief_summaries: list,
    start_date,
    end_date,
    model: str = "gpt-4o"
) -> str:
    prompt_context = {
        "start_date": start_date,
        "end_date": end_date,
        "summaries": brief_summaries,
    }
    prompt = load_prompt("weekly_report_prompt.j2", prompt_context)
    print(prompt)
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "너는 기간별 인사이트 리포트 전문 에디터야."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1800,
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()
