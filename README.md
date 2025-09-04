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
Run the full stack (frontend, backend, and MinIO storage) using Docker Compose:

```bash
docker compose up --build
```

Services started:
- **frontend** – Next.js app on `localhost:3000`
- **backend** – Express API on `localhost:4000` with a `/storage` volume for uploads and job data
- **minio** – S3-compatible storage on `localhost:9000` (user `minio`, password `minio123`)

Stop the stack with `docker compose down`.

## Environment Variables

The stack is configured through the following environment variables:

| Variable | Description |
| --- | --- |
| `OPENAI_API_KEY` | API key used by the backend for OpenAI requests. |
| `NEXT_PUBLIC_API_URL` | URL of the backend exposed to the frontend. Docker Compose sets this to `http://backend:4000`. |
| `IMAGE_BACKEND` | Feature flag to select the image generation backend: `openai` (default) or `sd`. |
| `SD_URL` | URL of the Stable Diffusion `txt2img` endpoint when `IMAGE_BACKEND=sd`. |

## Testing and Linting
```bash
npm test              # placeholder tests for Next.js app
npm run lint          # ESLint
npm --prefix api test # placeholder tests for API
```

## Image Generation Backend

The FastAPI app in `app/` can produce illustrations for each audio segment. By default it uses the OpenAI Images API, but it can also query a local Stable Diffusion server.

Environment variables:

- `IMAGE_BACKEND`: set to `openai` (default) or `sd` to use a Stable Diffusion API.
- `SD_URL`: URL of the Stable Diffusion `txt2img` endpoint (defaults to `http://localhost:7860/sdapi/v1/txt2img`).

Images are saved under `/storage/{jobId}/images/{segmentId}.png` and the served URLs are recorded in the job's `segments.json` file.

## License
MIT
