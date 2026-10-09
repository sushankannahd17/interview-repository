# Placement Intelligence Platform

## Services

- **FastAPI API** accepts internal ingestion requests, exposes processing status, and provides the preparation, search, and agent endpoints.
- **RabbitMQ worker** consumes experience IDs and runs the extraction, normalization, classification, resolution, and persistence pipeline.
- **Supabase** stores raw experiences and canonical entities. The SQL in `sql/master_schema.sql` defines the expected schema and indexes.
- **React console** in `frontend/` provides a local interface for trying the AI endpoints.

## Run locally

1. Copy `.env.example` to `.env` and set Supabase credentials, RabbitMQ URL, internal API key, and model credentials.
2. Start the API, worker, and RabbitMQ with `docker compose up --build`.
3. Start the console from `frontend/` with `pnpm install` and `pnpm dev`.
4. Apply the SQL schema to the configured Supabase project before processing experiences.

## Internal API protection

Ingestion and status routes require the `X-Internal-Api-Key` header. Configure the same key for the API and its caller. Browser origins for the console are controlled by `CORS_ALLOWED_ORIGINS`.

## Operational notes

- The worker queue is durable and rejected messages are routed to a durable dead-letter queue. Inspect dead-letter messages when processing repeatedly fails.
- `AMQP_QUEUE` defaults to `exp_queue_v2` so deployments can migrate from the earlier non-durable queue without redeclaring it with incompatible settings.
- The API health endpoint does not prove that Supabase or RabbitMQ is reachable; check container logs and the internal status endpoint when diagnosing processing.
- Run the test suite with `uv run --with-requirements requirements.txt -- python -m pytest -q`.
