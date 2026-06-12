# AI-Powered Transaction Processing Pipeline

This project is a production-grade backend service designed to process transactions from CSV files, clean the data, detect anomalies using a rules engine, and classify uncategorized transactions using a large language model (Google Gemini).

## Architecture

- **Backend**: FastAPI (Python 3.12)
- **Database**: PostgreSQL (SQLAlchemy 2.0, Alembic)
- **Queue/Workers**: Celery with Redis broker
- **Data Processing**: Pandas
- **AI**: Google GenAI (Gemini 1.5 Flash)
- **Containerization**: Docker & Docker Compose

## Requirements

- Docker & Docker Compose installed.
- Gemini API Key (or fallback to mock behavior).

## Setup & Running

1. Copy the environment configuration file:
   ```bash
   cp .env.example .env
   ```
2. Update the `.env` file with your `GEMINI_API_KEY`.
3. Build and run using Docker Compose:
   ```bash
   docker-compose up --build
   ```

This will bring up the `api` (port 8000), `worker`, `postgres` (port 5432), and `redis` (port 6379).
Alembic migrations are automatically applied on startup.

## Testing

To run the unit tests, ensure you have the required dependencies and run `pytest`:

```bash
pip install -r requirements.txt
pytest
```

## API Endpoints

- `GET /health` : Verify system health
- `POST /api/v1/jobs/upload` : Upload a CSV for asynchronous processing
- `GET /api/v1/jobs/{job_id}/status` : Get the status of a job
- `GET /api/v1/jobs/{job_id}/results` : Get transactions, anomalies, and AI summary
- `GET /api/v1/jobs` : List recent jobs
