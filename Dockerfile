FROM python:3.11-slim

WORKDIR /app

COPY ./server ./server

RUN pip install --no-cache-dir fastapi uvicorn

EXPOSE 80

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "80"]