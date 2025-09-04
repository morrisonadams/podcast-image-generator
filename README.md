# Podcast Image Generator

A baseline project that combines a Next.js frontend with an Express API. The API exposes endpoints for audio uploads and GPT-powered responses, while the frontend is a minimal Next.js scaffold.

## Prerequisites
- Node.js 18+
- An OpenAI API key available as `OPENAI_API_KEY` for the `/gpt` endpoint

## Local Development
Install dependencies for both the frontend and API:

```bash
npm install
npm --prefix api install
```

Start the development servers:

```bash
npm run dev            # Next.js on http://localhost:3000
npm --prefix api dev   # Express API on http://localhost:4000
```

## Docker
Run the full stack (web, API, and MinIO storage) using Docker Compose:

```bash
docker compose up --build
```

Services started:
- **web** – Next.js app on `localhost:3000`
- **api** – Express API on `localhost:4000`
- **minio** – S3-compatible storage on `localhost:9000` (user `minio`, password `minio123`)

Stop the stack with `docker compose down`.

## Testing and Linting
```bash
npm test              # placeholder tests for Next.js app
npm run lint          # ESLint
npm --prefix api test # placeholder tests for API
```

## License
MIT
