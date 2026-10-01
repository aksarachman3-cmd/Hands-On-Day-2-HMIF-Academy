from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import csv, io
from ai.optimizer import optimize_routes

app = FastAPI()
templates = Jinja2Templates(directory="frontend/templates")

orders = []
pickers = [
    {"picker_id": 1, "name": "Andi", "status": "available"},
    {"picker_id": 2, "name": "Budi", "status": "available"}
]
tasks = []

@app.post("/orders/import")
async def import_orders(file: UploadFile = File(...)):
    content = await file.read()
    reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
    global orders
    orders = [row for row in reader]
    return {"status": "ok", "count": len(orders)}

@app.post("/optimize")
async def optimize():
    global tasks
    try:
        result = optimize_routes(orders, pickers)
        tasks = result["tasks"]
        return {"status": "ok", "tasks": tasks, "confidence": result["confidence"]}
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.get("/picker/{picker_id}/tasks")
async def get_tasks(picker_id: int):
    return [t for t in tasks if t["picker_id"] == picker_id]

@app.post("/tasks/{task_id}/complete")
async def complete_task(task_id: int):
    for t in tasks:
        if t["task_id"] == task_id:
            t["status"] = "completed"
            return {"status": "ok"}
    return JSONResponse(status_code=404, content={"error": "Task not found"})

@app.get("/supervisor", response_class=HTMLResponse)
async def supervisor_page(request: Request):
    return templates.TemplateResponse(request=request, name="supervisor.html")

@app.get("/picker/{picker_id}", response_class=HTMLResponse)
async def picker_page(request: Request, picker_id: int):
    return templates.TemplateResponse(request=request, name="picker.html", context={"picker_id": picker_id})