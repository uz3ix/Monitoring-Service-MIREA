FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /service/backend
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt && useradd --create-home appuser
COPY app ./app

COPY migrations ./migrations
COPY alembic.ini .

USER appuser
EXPOSE 8000

CMD ["sh", "-c", "python -m alembic upgrade head && exec python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"]

