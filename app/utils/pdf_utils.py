import io
import re
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from typing import List, Tuple

def convert_pdf_to_html(pdf_path: str) -> str:
    output = io.StringIO()
    laparams = LAParams()
    with open(pdf_path, "rb") as fp:
        extract_text_to_fp(fp, output, laparams=laparams, output_type="html", codec=None)
    return output.getvalue()

def extract_page_map(html_str: str) -> dict:
    page_pattern = re.compile(r'<a name="(\d+)">Page \1</a>', re.MULTILINE)
    page_positions = [(m.start(), int(m.group(1))) for m in page_pattern.finditer(html_str)]
    page_positions.append((len(html_str), None))

    page_map = {}
    for i in range(len(page_positions) - 1):
        start_pos = page_positions[i][0]
        end_pos = page_positions[i + 1][0]
        page_num = page_positions[i][1]
        page_map[page_num] = html_str[start_pos:end_pos]
    return page_map

def detect_post_ranges(page_map: dict) -> List[Tuple[str, int, int]]:
    # 좌표·태그 구조는 유지하되, top/left 값 및 개행, 공백 등은 느슨하게 허용
    post_pattern = re.compile(
        r'<div[^>]*?left\s*:\s*3[01]\d?px;[^>]*?top\s*:\s*\d+px;[^>]*?>'
        r'.{0,300}?(\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}).{0,200}?</div>'
        r'.{0,1000}?<div[^>]*?left\s*:\s*34\d?px;[^>]*?top\s*:\s*\d+px;[^>]*?>'
        r'.{0,300}?(http://blog\.naver\.com/[^\s<]+)',
        re.DOTALL | re.IGNORECASE
    )

    page_posts = {}
    for page, html_chunk in page_map.items():
        match = post_pattern.search(html_chunk)
        if match:
            _, blog_url = match.groups()
            post_id = blog_url.replace("http://blog.naver.com/", "")
            page_posts[page] = post_id

    # 페이지 순서대로 정렬 후 포스트 범위 계산
    post_ranges = []
    current_post = None
    start_page = None
    sorted_pages = sorted(page_map.keys())

    for page in sorted_pages:
        if page in page_posts:
            if current_post is not None:
                post_ranges.append((current_post, start_page, page - 1))
            current_post = page_posts[page]
            start_page = page

    if current_post is not None:
        post_ranges.append((current_post, start_page, sorted_pages[-1]))

    return post_ranges