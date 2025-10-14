import json

def extract_body_from_json(json_path: str) -> str:
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("body", "")
    except Exception as e:
        import logging
        logging.warning(f"[WARN] body 파싱 실패: {e}")
        return ""
