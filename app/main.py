from pathlib import Path
import sys
import json

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from fastapi import FastAPI
from pydantic import BaseModel

from app.ask import answer_question, load_knowledge_base
from app.data_processing import process_tickets
from app.metrics import build_summary_metrics

app = FastAPI(title="AI Support Ticket Analyzer")

df = process_tickets(ROOT_DIR / "tickets.csv")
knowledge_base = load_knowledge_base(ROOT_DIR / "app" / "knowledge_base.md")


class AskRequest(BaseModel):
    question: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/summary")
def summary():
    return build_summary_metrics(df)


@app.get("/tickets")
def tickets(limit: int = 20):
    return json.loads(df.head(limit).to_json(orient="records", date_format="iso"))


@app.post("/ask")
def ask(request: AskRequest):
    answer = answer_question(request.question, df, knowledge_base)
    return {"question": request.question, "answer": answer}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
