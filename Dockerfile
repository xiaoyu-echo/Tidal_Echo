FROM python:3.11-slim

WORKDIR /app

COPY backend/ ./backend/
COPY examples/ ./examples/

RUN pip install -r backend/requirements.txt

WORKDIR /app/backend

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
