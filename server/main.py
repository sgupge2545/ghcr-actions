from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

app = FastAPI()


@app.get("/api/hello")
def read_root():
    return {"message": "Hello, World!"}


app.mount("/", StaticFiles(directory="server/dist", html=True), name="static")
