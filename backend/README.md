# Backend Application

FastAPI backend for AI-Powered Talent Scouting & Engagement Agent.

## Quick Start

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## Deployment (Render)

Render uses a dynamic port. Use:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### CORS (important for Vercel)

By default, the backend allows:

- `http://localhost:3000`
- `https://*.vercel.app` (via regex)

You can override with:

- `CORS_ALLOW_ORIGINS` (comma-separated)
- `CORS_ALLOW_ORIGIN_REGEX`

## API Endpoints

- `GET /api/health` - Health check endpoint
- `GET /api/talents` - List all talents
- `GET /api/talents/{id}` - Get talent by ID

## Project Structure

```
backend/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Core configuration
│   ├── data/         # JSON data files
│   └── main.py       # Application entry point
├── requirements.txt
└── .env
```