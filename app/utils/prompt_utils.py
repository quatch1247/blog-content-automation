from jinja2 import Environment, FileSystemLoader
from app.core.config import get_settings

settings = get_settings()

def load_prompt(template_name: str, context: dict) -> str:
    env = Environment(
        loader=FileSystemLoader(f"{settings.base_dir}/prompts"),
        autoescape=False
    )
    template = env.get_template(template_name)
    return template.render(context)
