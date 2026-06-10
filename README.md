# AccessibilityTracker (working title)

A discovery tool for querying Google Maps Places API and filtering by wheelchair-accessible locations.

## The problem

Google lets owners report wheelchair accessibility (entrance, washroom, parking, seating), but that data is not easy to search. You usually have to open each place and look for the ♿ symbol. This project geocodes an area, finds nearby places by type, scores them from Google's accessibility fields, and returns a ranked list.

## Prerequisites

- Python 3.10+ (Dockerfile uses 3.10)
- [Google Maps API key](https://developers.google.com/maps/documentation/places/web-service/get-api-key) with **Places API (New)** enabled

## Setup

1. Clone the repo and go to the backend:

   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Create `backend/.env` from the example:

   ```bash
   cp .env.example .env
   ```

3. Set your key in `backend/.env`:

   ```env
   GOOGLE_MAPS_API_KEY=your_key_here
   ```

   The app loads env from **`backend/.env`** (path is resolved relative to the config module, not your shell cwd).

## Run locally

From `backend/` with the venv active:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- App root: http://127.0.0.1:8000/
- **Swagger UI:** http://127.0.0.1:8000/docs
- **OpenAPI JSON:** http://127.0.0.1:8000/openapi.json

Use `127.0.0.1:8000` in the browser; `0.0.0.0` is the bind address only.

## Run with Docker

From the repo root (export `GOOGLE_MAPS_API_KEY` in your shell or use a root `.env` for Compose):

```bash
docker compose up --build
```

Same URLs on port **8000**.

## API overview

All versioned routes live under **`/api/v1`**. A convenience alias exists at **`GET /health`** (same response as `/api/v1/health`).

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check (alias) |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/geocode?query=...` | Geocode via OpenStreetMap Nominatim |
| POST | `/api/v1/search` | Search accessible places near a query |

### Search request

`radius` is in **meters** (Google `searchNearby` circle radius). Default **1000**, allowed range **100–50000**.

```json
{
  "query": "Connaught Place, New Delhi, Delhi",
  "radius": 1500,
  "place_type": "restaurant",
  "accessibility_priorities": {
    "wheelchair_accessible_entrance": 3,
    "wheelchair_accessible_parking": 2,
    "wheelchair_accessible_restroom": 2,
    "wheelchair_accessible_seating": 1
  }
}
```

- **`query`** — location text; the API geocodes it (you do not send lat/lng).
- **`place_type`** — one of: `restaurant`, `cafe`, `dentist`, `hospital`, `pharmacy`, `shopping_mall`, `gym`, `library`
- **`accessibility_priorities`** — optional; defaults shown above.

Results include only places with **`accessibility_score > 0`**, sorted by score then Google rating (descending).

## How scoring works

Each place is scored **0–10** from Google's wheelchair accessibility flags and your priority weights (defaults below).

| Feature | Default weight |
|---------|----------------|
| Entrance | 3 |
| Parking | 2 |
| Restroom | 2 |
| Seating | 1 |

**Formula:** `(earned weight ÷ total weight) × 10`, rounded to one decimal. Override weights in `accessibility_priorities` (each 0–5).

**Status** (from score, not feature count):

| Status | Score |
|--------|-------|
| Excellent | 7–10 |
| Partial | 4–6.9 |
| Limited | 0–3.9 |
| No data | No accessibility blob from Google (score 0) |

**Search results** only include places with **`accessibility_score > 0`**, so `no_data` venues and places where every flag is false are omitted.

## Example requests

Health:

```bash
curl -s http://127.0.0.1:8000/health | jq
curl -s http://127.0.0.1:8000/api/v1/health | jq
```

Geocode:

```bash
curl -sG "http://127.0.0.1:8000/api/v1/geocode" \
  --data-urlencode "query=Connaught Place, New Delhi, Delhi" | jq
```

Search:

```bash
curl -s -X POST http://127.0.0.1:8000/api/v1/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Khan Market, New Delhi, Delhi",
    "radius": 2000,
    "place_type": "cafe"
  }' | jq
```

Interactive testing: open http://127.0.0.1:8000/docs and use **POST /api/v1/search**.

## Sample responses

Responses below are illustrative; geocode text and search results depend on your query and what Google returns for that area.

### `GET /health`

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "message": "Accessibility Tracker API is running and ready to serve requests."
}
```

### `GET /geocode?query=Connaught Place, New Delhi, Delhi`

```json
{
  "latitude": 28.6315,
  "longitude": 77.2167,
  "display_name": "Connaught Place, New Delhi, Delhi, India"
}
```

### `POST /search`

Example for the Khan Market curl above. Array of places with **`accessibility_score > 0`**, highest score first.

```json
[
  {
    "display_name": {
      "text": "Example Cafe",
      "languageCode": "en"
    },
    "formatted_address": "Middle Lane, Khan Market, New Delhi, Delhi 110003, India",
    "location": {
      "latitude": 28.6004,
      "longitude": 77.2270
    },
    "rating": 4.5,
    "user_rating_count": 812,
    "accessibility_options": {
      "wheelchair_accessible_parking": true,
      "wheelchair_accessible_entrance": true,
      "wheelchair_accessible_restroom": true,
      "wheelchair_accessible_seating": true
    },
    "accessibility_score": 10.0,
    "accessibility_status": "excellent",
    "accessibility_breakdown": {
      "wheelchair_accessible_entrance": true,
      "wheelchair_accessible_parking": true,
      "wheelchair_accessible_restroom": true,
      "wheelchair_accessible_seating": true
    }
  },
  {
    "display_name": {
      "text": "Example Restaurant",
      "languageCode": "en"
    },
    "formatted_address": "Rajiv Chowk, Connaught Place, New Delhi, Delhi 110001, India",
    "location": {
      "latitude": 28.6328,
      "longitude": 77.2197
    },
    "rating": 4.2,
    "user_rating_count": 540,
    "accessibility_options": {
      "wheelchair_accessible_parking": true,
      "wheelchair_accessible_entrance": false,
      "wheelchair_accessible_restroom": true,
      "wheelchair_accessible_seating": false
    },
    "accessibility_score": 5.0,
    "accessibility_status": "partial",
    "accessibility_breakdown": {
      "wheelchair_accessible_entrance": false,
      "wheelchair_accessible_parking": true,
      "wheelchair_accessible_restroom": true,
      "wheelchair_accessible_seating": false
    }
  }
]
```

## Project layout

```
backend/app/
  main.py              FastAPI app, CORS, routers
  apis/v1/search.py    /health, /geocode, /search
  schemas/             Pydantic request/response models
  services/            geocoding, Google Places, normalize
  core/config.py       Settings (GOOGLE_MAPS_API_KEY)
```

## Data source

Powered by **[Google Places API (New)](https://developers.google.com/maps/documentation/places/web-service/op-overview)** for nearby search and accessibility fields, and **[OpenStreetMap Nominatim](https://nominatim.org/)** for geocoding location queries.

## Notes

- Accessibility scores reflect **Google's self-reported fields**, not on-site verification.
- Google returns at most **20** nearby places per search; venues with no positive accessibility signal are omitted from results.

## TODO

- [ ] Frontend (React form + results)
- [ ] Tests (pytest + mocks)
- [ ] `min_score` filtering
- [ ] Async HTTP (httpx)
