from fastapi import FastAPI

from graph import run_query
from models import AskRequest, AskResponse


app = FastAPI(
    title="Zepto Support Assistant",
    description="RAG-based Zepto policy support assistant",
    version="1.0.0",
)


@app.get("/")
def home():
    return {
        "message": "Zepto Support Assistant is running!"
    }


@app.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):

    response = run_query(request.query)

    return response