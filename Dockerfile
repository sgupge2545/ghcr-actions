FROM node:24.1.0 AS client-build
WORKDIR /client
COPY ./client ./
RUN npm install && npm run build && ls -l dist

FROM python:3.11-slim

WORKDIR /app

# FastAPI用ソース
COPY ./server ./server

# Reactビルド成果物をserver/distにコピー
COPY --from=client-build /client/dist ./server/dist

RUN pip install --no-cache-dir -r server/requirements.txt

EXPOSE 80

CMD ["uvicorn", "server.main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]

LABEL org.opencontainers.image.source https://github.com/kiei/mpec