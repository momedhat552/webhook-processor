# Webhook Processor

A small REST API built with FastAPI that receives alerts from external systems, simulates heavy processing (3-second delay), stores them in SQLite, and lets you retrieve them.

## Endpoints

| Method | Path       | Description                                           |
|--------|------------|-------------------------------------------------------|
| POST   | `/webhook` | Receive an alert (JSON), process it, and store it     |
| GET    | `/alerts`  | Return a list of all processed alerts                 |

Example alert:

```json
{
  "event_id": "evt_98765",
  "source": "server_1",
  "message": "High CPU",
  "timestamp": "2026-11-11T08:00:00Z"
}
```

## Live deployment

The app is deployed on an AWS EC2 instance (Ubuntu, Docker Compose):

- Base URL: http://13.60.214.14:8000
- Swagger docs: http://13.60.214.14:8000/docs
- Stored alerts: http://13.60.214.14:8000/alerts

Note: the demo server has no TLS certificate, so use `http://`, not `https://`. Your browser may show a "Not secure" warning, which is expected.

## Run with Docker  

Requirements: Docker and Docker Compose.

```bash
git clone https://github.com/momedhat552/webhook-processor
cd webhook-processor
docker compose up --build
```

The API is then available at `http://localhost:8000`.
Interactive docs (Swagger UI): `http://localhost:8000/docs`

Data is stored in a SQLite file inside a Docker volume (`alerts_data`), so alerts survive container restarts. To stop the app, press `Ctrl+C` (or run `docker compose down`).

## Test the endpoints

Send an alert (takes about 3 seconds because of the simulated processing):

```bash
curl -X POST http://localhost:8000/webhook -H "Content-Type: application/json" -d "@alert.json"
```

Expected response:

```json
{"status": "processed", "event_id": "evt_98765"}
```

List all processed alerts:

```bash
curl http://localhost:8000/alerts
```

On Windows PowerShell, use `curl.exe` instead of `curl`.

Invalid payloads (for example a missing field) return `422 Unprocessable Entity`.

## Run locally without Docker

```bash
python -m venv venv
venv\Scripts\activate        # Linux/macOS: source venv/bin/activate
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

## Design notes

- **Validation:** Pydantic model checks every incoming alert has `event_id`, `source`, `message`, and `timestamp`.
- **Processing delay:** `await asyncio.sleep(3)` in an async endpoint, so one slow request does not block the server.
- **Storage:** SQLite. No extra service is needed, and it is persisted with a Docker volume.
- **Idempotency:** `event_id` is the primary key and inserts use `INSERT OR REPLACE`, so a retried webhook with the same `event_id` does not create duplicates.

