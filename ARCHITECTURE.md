# Architecture

## Layers
- **Presentation**: HTML + Tailwind CDN (supervisor.html, picker.html)
- **Logic/Business**: FastAPI (backend/main.py)
- **AI/Logic Core**: Python heuristic (ai/optimizer.py) — velocity, affinity, batching, routing
- **Data**: In-memory (orders, pickers, tasks)
- **External Service**: None — AI runs locally, no external API

## Flow
1. Supervisor upload CSV → `POST /orders/import`
2. Trigger optimize → `POST /optimize` → AI module
3. Picker views tasks → `GET /picker/{id}/tasks`
4. Complete task → `POST /tasks/{id}/complete`

## Tech Stack
| Layer | Tech | Reason |
|-------|------|--------|
| Backend | FastAPI | Fast, auto docs at /docs |
| Frontend | HTML + Tailwind CDN | No build step, quick |
| AI | Python heuristic | Runs locally, no external API |
| Data | In-memory | Demo only, no DB setup |

## Data Entities
- **Order**: order_id, sku, bin_location, qty
- **Picker**: picker_id, name, status
- **Task**: task_id, order_id, sequence, status, qty

## AI Workflow (summary)
1. Compute SKU velocity (frequency) and affinity (co-occurrence).
2. Group orders by bin.
3. Sort bins by total SKU velocity (faster-mover first).
4. Assign bins to pickers round-robin.
5. Confidence = ratio of bins with >1 order (batched) / total bins.

See [docs/AI_WORKFLOW.md](docs/AI_WORKFLOW.md) for details.

## Failure Handling
- Empty orders → `ValueError`
- Missing `bin_location` → `ValueError` "Digitasi bin diperlukan"
- Empty CSV → HTTP 400
- Missing required columns → HTTP 400