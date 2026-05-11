import time
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import create_agent_executor

load_dotenv()

app = FastAPI(title="TailorTalk Drive Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

executor = create_agent_executor()
chat_history = []
metrics = {
    "total_queries": 0,
    "successful_queries": 0,
    "failed_queries": 0,
    "total_response_time": 0.0,
    "query_log": []
}

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    response_time_ms: int
    success: bool

class MetricsResponse(BaseModel):
    total_queries: int
    successful_queries: int
    failed_queries: int
    success_rate: float
    avg_response_time_ms: float
    query_log: list

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics", response_model=MetricsResponse)
def get_metrics():
    total = metrics["total_queries"]
    avg_time = (
        metrics["total_response_time"] / total if total > 0 else 0
    )
    success_rate = (
        metrics["successful_queries"] / total * 100 if total > 0 else 0
    )
    return MetricsResponse(
        total_queries=total,
        successful_queries=metrics["successful_queries"],
        failed_queries=metrics["failed_queries"],
        success_rate=round(success_rate, 1),
        avg_response_time_ms=round(avg_time, 1),
        query_log=metrics["query_log"][-20:],
    )

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Empty message")

    start = time.time()
    metrics["total_queries"] += 1
    success = False

    try:
        result = executor.invoke({
            "input": req.message,
            "chat_history": chat_history,
        })
        response = result["output"]
        chat_history.append({"role": "user", "content": req.message})
        chat_history.append({"role": "assistant", "content": response})
        success = True
        metrics["successful_queries"] += 1
    except Exception as e:
        response = f"Error: {str(e)}"
        metrics["failed_queries"] += 1

    elapsed_ms = int((time.time() - start) * 1000)
    metrics["total_response_time"] += elapsed_ms

    metrics["query_log"].append({
        "query": req.message,
        "success": success,
        "response_time_ms": elapsed_ms,
    })

    return ChatResponse(
        response=response,
        response_time_ms=elapsed_ms,
        success=success,
    )

@app.delete("/chat")
def clear_memory():
    chat_history.clear()
    return {"status": "cleared"}