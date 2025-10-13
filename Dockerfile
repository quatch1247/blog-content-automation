FROM python:3.10-slim

# 필수 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# 작업 디렉토리
WORKDIR /app

# Poetry 설치
RUN pip install --no-cache-dir poetry

# Poetry 관련 파일 복사
COPY poetry.lock pyproject.toml /app/

# Poetry 가상환경 비활성화 & 의존성 설치
RUN poetry config virtualenvs.create false \
 && poetry install --no-root --only main

# 전체 프로젝트 복사
COPY . /app

# FastAPI 서버 실행
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
