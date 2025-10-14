FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev shared-mime-info fonts-noto-cjk libgobject-2.0-0 \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false \
 && poetry install --no-root --only main

COPY . /app

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
