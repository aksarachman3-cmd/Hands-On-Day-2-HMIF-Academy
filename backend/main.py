from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
import csv
import io
from ai.optimizer import optimize_routes

app = FastAPI(
    title="PickWise AI",
    description="AI-powered picking route optimization for manual e-commerce warehouses",
    version="1.0.0"
)

templates = Jinja2Templates(directory="frontend/templates")

# In-memory data store (demo only)
orders = []
pickers = [
    {"picker_id": 1, "name": "Andi", "status": "available"},
    {"picker_id": 2, "name": "Budi", "status": "available"}
]
tasks = []


# ---------------- Health Check ----------------
@app.get("/health")
async def health():
    return {
        "status": "ok",
        "orders": len(orders),
        "tasks": len(tasks),
        "pickers": len(pickers)
    }


# ---------------- Order Import ----------------
@app.post("/orders/import")
async def import_orders(file: UploadFile = File(...)):
    try:
        content = await file.read()
        reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
        rows = list(reader)
    except Exception as e:
        return JSONResponse(status_code=400, content={"error": f"Gagal membaca CSV: {str(e)}"})

    if not rows:
        return JSONResponse(status_code=400, content={"error": "File CSV kosong"})

    required = {'order_id', 'sku', 'bin_location', 'qty'}
    if not required.issubset(rows[0].keys()):
        missing = required - set(rows[0].keys())
        return JSONResponse(
            status_code=400,
            content={"error": f"Kolom wajib tidak ditemukan: {missing}"}
        )

    global orders
    orders = rows
    return {"status": "ok", "count": len(orders)}


# ---------------- Optimize Routes ----------------
@app.post("/optimize")
async def optimize():
    global tasks
    try:
        result = optimize_routes(orders, pickers)
        tasks = result["tasks"]
        return {
            "status": "ok",
            "tasks": tasks,
            "confidence": result["confidence"],
            "velocity": result["velocity"],
            "affinity_pairs": result["affinity_pairs"]
        }
    except ValueError as e:
        return JSONResponse(status_code=400, content={"error": str(e)})


# ---------------- Picker Tasks ----------------
@app.get("/picker/{picker_id}/tasks")
async def get_tasks(picker_id: int):
    return [t for t in tasks if t["picker_id"] == picker_id]


@app.post("/tasks/{task_id}/complete")
async def complete_task(task_id: int):
    for t in tasks:
        if t["task_id"] == task_id:
            t["status"] = "completed"
            return {"status": "ok", "task_id": task_id}
    return JSONResponse(status_code=404, content={"error": "Task not found"})


# ---------------- Frontend Pages ----------------
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return HTMLResponse(
        content='<h1>PickWise AI</h1>'
                '<p>Buka <a href="/supervisor">/supervisor</a> atau '
                '<a href="/picker/1">/picker/1</a></p>'
                '<p>API docs: <a href="/docs">/docs</a></p>'
    )


@app.get("/supervisor", response_class=HTMLResponse)
async def supervisor_page(request: Request):
    return templates.TemplateResponse(request=request, name="supervisor.html")


@app.get("/picker/{picker_id}", response_class=HTMLResponse)
async def picker_page(request: Request, picker_id: int):
    return templates.TemplateResponse(
        request=request,
        name="picker.html",
        context={"picker_id": picker_id}
    )