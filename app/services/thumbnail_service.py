import base64
from openai import OpenAI
from fastapi import HTTPException
from app.core.db import get_db_session
from app.repositories import pdf_repository
from app.utils.storage_utils import extract_body_from_json
from app.core.config import get_settings
from app.utils.prompt_utils import load_prompt

settings = get_settings()

class ThumbnailService:
    @staticmethod
    def generate_thumbnail_info(post_id: int) -> dict:
        db = get_db_session()
        try:
            post = pdf_repository.get_refined_post_basic_by_id(db, post_id)
            if not post:
                raise HTTPException(status_code=404, detail="해당 RefinedPost를 찾을 수 없습니다.")

            title = post["title"] or ""
            author = post["author"] or ""
            json_path = post["json_path"]
            body = extract_body_from_json(json_path)

            prompt_context = {
                "title": title,
                "author": author,
                "body": body,
            }

            prompt = load_prompt("thumbnail_prompt.j2", prompt_context)
            # print("프롬프트:", prompt)

            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            resp = client.images.generate(
                model="gpt-image-1",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="high",
                output_format="png",
            )

            if not resp or not resp.data or len(resp.data) == 0:
                raise HTTPException(status_code=500, detail="Image generation failed, no data returned")

            image_bytes = base64.b64decode(resp.data[0].b64_json)

            return {
                "image_bytes": image_bytes,
                "filename": f"thumbnail_{post_id}.png",
                "title": title,
                "post_id": post_id,
                "prompt": prompt,
            }
        finally:
            db.close()
