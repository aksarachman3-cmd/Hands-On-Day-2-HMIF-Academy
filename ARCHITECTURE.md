# Architecture

## Layers
- **Presentation**: HTML + Tailwind CDN
- **Logic/Business**: FastAPI
- **AI/Logic Core**: Python heuristic (batching + routing)
- **Data**: In-memory (demo only)
- **External Service**: None

## Flow
1. Supervisor uploads CSV → `POST /orders/import`
2. Trigger optimize → `POST /optimize` → AI module
3. Picker views tasks → `GET /picker/{id}/tasks`
4. Complete task → `POST /tasks/{id}/complete`

## Tech Stack
| Layer | Tech | Reason |
|-------|------|--------|
| Backend | FastAPI | Fast, auto docs |
| Frontend | HTML + Tailwind | No build step |
| AI | Python | Runs locally |
| Data | In-memory | Demo only |

## Data Entities
- Order: order_id, sku, bin_location, qty
- Picker: picker_id, name, status
- Task: task_id, order_id, sequence, status