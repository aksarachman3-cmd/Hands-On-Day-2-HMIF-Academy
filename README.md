# PickWise AI

AI-powered picking route optimization for manual e-commerce warehouses.

## How to Run (3 steps)
1. `pip install -r requirements.txt`
2. `uvicorn backend.main:app --reload`
3. Open `http://localhost:8000/supervisor` and `http://localhost:8000/picker/1`

## Demo
- Input: `/demo/input_orders.csv`
- Output: `/demo/output_routes.json`

## Architecture
See [ARCHITECTURE.md](ARCHITECTURE.md)

## AI Workflow
See [docs/AI_WORKFLOW.md](docs/AI_WORKFLOW.md)

## Testing
See [docs/TESTING.md](docs/TESTING.md)

## Screenshots
- Mockups (Stitch): `/docs/screenshots/supervisor_mockup.png`, `/docs/screenshots/picker_mockup.png`
- Implementation: `/docs/screenshots/supervisor.png`, `/docs/screenshots/picker.png`

## Tech Stack
- Backend: FastAPI
- Frontend: HTML + Tailwind CDN
- AI: Python heuristic (velocity, affinity, batching, routing)
- Data: In-memory

## API Endpoints
| Method | Path | Description |
|--------|------|-------------|
| POST | `/orders/import` | Upload CSV orders |
| POST | `/optimize` | Run AI optimization |
| GET | `/picker/{id}/tasks` | Get tasks for picker |
| POST | `/tasks/{id}/complete` | Mark task complete |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |