# AI-Powered Transaction Processing Pipeline

This project is a production-grade backend service designed to process transactions from CSV files, clean the data, detect anomalies using a rules engine, and classify uncategorized transactions using a large language model (OpenAI).

## Live Demo

- **API Base URL**: [http://43.204.142.128:8000](http://43.204.142.128:8000)
- **Swagger Documentation**: [http://43.204.142.128:8000/docs](http://43.204.142.128:8000/docs)

## Architecture

- **Backend**: FastAPI (Python 3.12)
- **Database**: PostgreSQL (SQLAlchemy 2.0, Alembic)
- **Queue/Workers**: Celery with Redis broker
- **Data Processing**: Pandas
- **AI**: OpenAI (GPT-3.5 Turbo)
- **Containerization**: Docker & Docker Compose

## Requirements

- Docker & Docker Compose installed.
- OpenAI API Key (or fallback to mock behavior).

## Setup & Running

1. Copy the environment configuration file:
   ```bash
   cp .env.example .env
   ```
2. Update the `.env` file with your `OPENAI_API_KEY` and set `LLM_PROVIDER=openai`.
3. Build and run using Docker Compose:
   ```bash
   docker-compose up --build
   ```

This will bring up the `api` (port 8000), `worker`, `postgres` (port 5432), and `redis` (port 6379).
Alembic migrations are automatically applied on startup.

### Deployment (AWS EC2)

The application is deployed to an AWS EC2 instance. To deploy changes:

1. SSH into the instance and pull the latest code.
2. Update the `.env` file (ensure `POSTGRES_PORT=5432` if running inside the Docker network).
3. Rebuild and restart the containers:
   ```bash
   sudo docker-compose up -d --build
   ```

## Testing

To run the unit tests, ensure you have the required dependencies and run `pytest`:

```bash
pip install -r requirements.txt
pytest
```

## API Endpoints

- `GET /health` : Verify system health
- `POST /jobs/upload` : Upload a CSV for asynchronous processing
- `GET /jobs/{job_id}/status` : Get the status of a job
- `GET /jobs/{job_id}/results` : Get transactions, anomalies, and AI summary
- `GET /jobs` : List recent jobs

## Example Usage (cURL)

**1. Upload a CSV File**

_Note: You can test the API using the included `test_sample.csv`, or `large_transactions.csv` files._

```bash
curl -X POST "http://43.204.142.128:8000/jobs/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_sample.csv"
```

_(This returns a `job_id` like `d9936632-0172-486f-a721-4b6da4b51ebc`)_

**2. Check Job Status**

```bash
curl -X GET "http://43.204.142.128:8000/jobs/d9936632-0172-486f-a721-4b6da4b51ebc/status"
```

**3. Get Job Results (Anomalies & AI Summary)**

```bash
curl -X GET "http://43.204.142.128:8000/jobs/d9936632-0172-486f-a721-4b6da4b51ebc/results"
```
