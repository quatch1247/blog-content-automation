import io
import markdown
from weasyprint import HTML
from fastapi import HTTPException
from contextlib import closing
from app.repositories import pdf_repository
from app.core.db import get_db_session

class SummaryService:
    @staticmethod
    def generate_summary_pdf(post_id: int) -> dict:
        with closing(get_db_session()) as db:
            md_text = pdf_repository.get_summary_markdown_by_post_id(db, post_id)
            if not md_text:
                raise HTTPException(status_code=404, detail="요약문이 존재하지 않습니다.")

        html_body = markdown.markdown(md_text)
        html = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
                body {{
                    font-family: 'Noto Sans KR', 'Pretendard', 'Apple SD Gothic Neo', sans-serif;
                    background: #f7faf7;
                    color: #212422;
                    margin: 0;
                    padding: 0;
                }}
                .container {{
                    max-width: 700px;
                    background: #fff;
                    margin: 48px auto 64px auto;
                    padding: 40px 32px 32px 32px;
                    border-radius: 22px;
                    box-shadow: 0 4px 28px rgba(80,180,80,0.08), 0 1.5px 4px rgba(0,0,0,0.06);
                    border: 1.5px solid #e5f9e0;
                }}
                h1 {{
                    font-size: 2.1em;
                    font-weight: 800;
                    letter-spacing: -1px;
                    margin-bottom: 18px;
                    border-bottom: 3px solid #7cfc8c33;
                    color: #24be4a;
                    padding-bottom: 8px;
                }}
                h2 {{
                    font-size: 1.28em;
                    color: #199f36;
                    margin-top: 38px;
                    margin-bottom: 8px;
                    border-bottom: 1.5px solid #dafee2;
                    padding-bottom: 6px;
                    font-weight: 700;
                }}
                h3, h4 {{
                    color: #198f34;
                    margin-top: 20px;
                }}
                p {{
                    font-size: 1.05em;
                    line-height: 1.85;
                    margin: 12px 0 10px 0;
                    color: #242a23;
                }}
                ul, ol {{
                    font-size: 1em;
                    margin: 8px 0 14px 22px;
                    padding-left: 1.2em;
                }}
                li {{
                    margin-bottom: 7px;
                }}
                .notice {{
                    background: #f0fff0;
                    color: #2a592e;
                    border-left: 5px solid #9ffca5;
                    border-radius: 8px;
                    padding: 12px 18px 12px 18px;
                    margin: 18px 0 18px 0;
                    font-size: 1.02em;
                }}
                .deadline {{
                    background: #e7ffe7;
                    border-left: 5px solid #8eea8f;
                    padding: 10px 18px;
                    margin: 20px 0;
                    border-radius: 8px;
                    font-weight: 500;
                    color: #28702d;
                }}
                code, pre {{
                    background: #f8fbf8;
                    border-radius: 5px;
                    padding: 4px 8px;
                    font-size: 1em;
                    color: #25892b;
                }}
                table {{
                    border-collapse: collapse;
                    margin: 18px 0;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #e2f5e7;
                    padding: 8px 14px;
                    font-size: 1em;
                }}
                th {{
                    background: #e8ffed;
                    color: #178a30;
                }}
                /* Extra touch for blockquote */
                blockquote {{
                    border-left: 4px solid #88eb8f;
                    background: #f7fff7;
                    color: #28823c;
                    margin: 20px 0 20px 0;
                    padding: 12px 18px;
                    font-style: italic;
                    border-radius: 7px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                {html_body}
            </div>
        </body>
        </html>
        """

        try:
            pdf_bytes = HTML(string=html).write_pdf()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"PDF 생성 중 오류 발생: {str(e)}")

        filename = f"summary_{post_id}.pdf"
        return {
            "pdf_bytes": pdf_bytes,
            "filename": filename,
        }
