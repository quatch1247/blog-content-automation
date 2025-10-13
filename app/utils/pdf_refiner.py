import os
import io
import json
import re
import fitz 
from pdfminer.high_level import extract_text_to_fp
from pdfminer.layout import LAParams
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor, as_completed

from app.core.exceptions import APIException
from app.core.error_codes import ErrorCode

def dedup_all_repeats(text, min_len=3):
    n = len(text)
    changed = True
    while changed:
        changed = False
        for l in range(n, min_len - 1, -1):
            substr_count = {}
            for i in range(n - l + 1):
                sub = text[i:i+l]
                cnt = text.count(sub)
                if cnt > 1:
                    substr_count[sub] = cnt
            if substr_count:
                sub = max(substr_count.keys(), key=len)
                first = text.find(sub)
                text = text[:first + len(sub)] + text[first + len(sub):].replace(sub, "")
                changed = True
                break
        n = len(text)
    return text

def rects_overlap(r1, r2):
    a = fitz.Rect(r1)
    b = fitz.Rect(r2)
    return a.intersects(b)

def extract_images(doc, save_dir):
    images = []
    for page_index in range(len(doc)):
        page = doc[page_index]
        link_rects = []
        for lnk in page.get_links():
            if lnk.get("kind", None) == 1 and "from" in lnk:
                link_rects.append(fitz.Rect(lnk["from"]))
        for img_index, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            img_info = page.get_image_info(xref)
            img_rect = fitz.Rect(img_info["bbox"]) if "bbox" in img_info else None
            if img_rect and any(rects_overlap(img_rect, lrect) for lrect in link_rects):
                continue
            imgdata = doc.extract_image(xref)
            ext = imgdata["ext"]
            img_bytes = imgdata["image"]
            img_name = f"img_{page_index+1}_{img_index+1}.{ext}"
            img_path = os.path.join(save_dir, img_name)
            with open(img_path, "wb") as f:
                f.write(img_bytes)
            images.append(img_path)
    return images

def convert_pdf_to_html(pdf_path):
    output = io.StringIO()
    laparams = LAParams()
    with open(pdf_path, "rb") as fp:
        extract_text_to_fp(fp, output, laparams=laparams, output_type="html", codec=None)
    return output.getvalue()

def extract_and_merge_text(pdf_path, temp_dir):
    html_content = convert_pdf_to_html(pdf_path)
    soup = BeautifulSoup(html_content, "html.parser")
    divs = soup.find_all("div", {"style": lambda s: s and "position:absolute" in s})
    lines = [div.get_text(strip=True) for div in divs if div.get_text(strip=True)]
    merged_text = "\n".join(lines).strip()
    merged_path = os.path.join(temp_dir, "__tmp_merged.txt")
    with open(merged_path, "w", encoding="utf-8") as f:
        f.write(merged_text)
    return merged_text, merged_path

def parse_merged_text_to_json(merged_txt_path, save_json_path):
    with open(merged_txt_path, 'r', encoding='utf-8') as f:
        lines = [line.rstrip('\n') for line in f]

    title   = dedup_all_repeats(lines[1] if len(lines) > 1 else '')
    author  = dedup_all_repeats(lines[2] if len(lines) > 2 else '')
    date    = lines[3] if len(lines) > 3 else ''
    url     = lines[4] if len(lines) > 4 else ''
    body_lines = lines[5:]

    clean_body_lines = []
    for i, line in enumerate(body_lines):
        if (line == "blog.naver.com" and i > 0 and re.search(r"\.\.\.$", body_lines[i-1])):
            if clean_body_lines: clean_body_lines.pop()
            continue
        if re.match(r"^Page\s*[\d:]*$", line) or re.match(r"^Page:[\d, ]+$", line) or re.match(r"^\d+·.*", line):
            continue
        clean_body_lines.append(line)
    body = '\n'.join([l for l in clean_body_lines if l.strip()])

    result = {
        "title": title,
        "author": author,
        "date": date,
        "url": url,
        "body": body
    }
    with open(save_json_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    return result

def process_pdf(pdf_path, output_base_dir):
    import traceback
    try:
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]
        post_dir = os.path.join(output_base_dir, base_name)
        os.makedirs(post_dir, exist_ok=True)
        images_dir = os.path.join(post_dir, "images")
        os.makedirs(images_dir, exist_ok=True)

        # 1. 이미지 추출
        try:
            doc = fitz.open(pdf_path)
            images = extract_images(doc, images_dir)
            images_rel = [os.path.relpath(img, post_dir) for img in images]
        except Exception as e:
            raise APIException(ErrorCode.PDF_PROCESSING_FAILED, details=[f"이미지 추출 오류: {e}"])

        # 2. 텍스트 병합(임시파일)
        try:
            merged_text, merged_path = extract_and_merge_text(pdf_path, post_dir)
        except Exception as e:
            raise APIException(ErrorCode.PDF_CONVERT_FAILED, details=[f"텍스트 병합 오류: {e}"])

        # 3. 2차 파싱 및 json 저장
        try:
            json_path = os.path.join(post_dir, f"{base_name}.json")
            parsed_json = parse_merged_text_to_json(merged_path, json_path)
        except Exception as e:
            raise APIException(ErrorCode.PDF_PROCESSING_FAILED, details=[f"2차 파싱 오류: {e}"])

        # 4. 병합 텍스트 임시 파일 삭제
        if os.path.exists(merged_path):
            os.remove(merged_path)

        post_info = {
            "images": images_rel,
            "parsed_json_path": json_path
        }

        return post_info

    except APIException as ae:
        raise
    except Exception as e:
        raise APIException(ErrorCode.PDF_PROCESSING_FAILED, details=[str(e)])

def batch_refine_split_posts(split_dir, output_dir, max_workers=2):
    pdf_files = [
        os.path.join(split_dir, fname)
        for fname in os.listdir(split_dir)
        if fname.lower().endswith(".pdf")
    ]
    os.makedirs(output_dir, exist_ok=True)

    results = []
    errors = []
    if max_workers > 1:
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_pdf = {executor.submit(process_pdf, pdf_path, output_dir): pdf_path for pdf_path in pdf_files}
            for future in as_completed(future_to_pdf):
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                except APIException as exc:
                    errors.append({"file": future_to_pdf[future], "error": exc.error.code, "details": exc.details})
    else:
        for pdf_path in pdf_files:
            try:
                result = process_pdf(pdf_path, output_dir)
                if result:
                    results.append(result)
            except APIException as exc:
                errors.append({"file": pdf_path, "error": exc.error.code, "details": exc.details})

    return {
        "success_count": len(results),
        "error_count": len(errors),
        "results": results,
        "errors": errors,
    }