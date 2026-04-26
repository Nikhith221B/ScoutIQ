# API Documentation

## Base URL

```
http://localhost:8000
```

## Endpoints

### Health Check

**GET** `/api/health`

Response:
```json
{
  "status": "healthy",
  "service": "AI-Powered Talent Scouting & Engagement Agent",
  "version": "0.1.0"
}
```

### List Talents

**GET** `/api/talents`

Response:
```json
[
  {
    "id": "1",
    "name": "Alex Johnson",
    "email": "alex.johnson@email.com",
    "phone": "+1-555-0101",
    "skills": ["Python", "Machine Learning", "Data Analysis"],
    "experience_years": 5,
    "location": "San Francisco, CA",
    "status": "active",
    "created_at": "2024-01-15T10:00:00Z"
  }
]
```

### Get Talent by ID

**GET** `/api/talents/{id}`

Response:
```json
{
  "id": "1",
  "name": "Alex Johnson",
  "email": "alex.johnson@email.com",
  "phone": "+1-555-0101",
  "skills": ["Python", "Machine Learning", "Data Analysis"],
  "experience_years": 5,
  "location": "San Francisco, CA",
  "status": "active",
  "created_at": "2024-01-15T10:00:00Z"
}
```

## Error Responses

- `404`: Talent not found
- `500`: Internal server error