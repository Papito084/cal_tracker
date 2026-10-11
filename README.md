# Cal Tracker

Cal Tracker is a lightweight **Calorie & Nutrition** tracking API built with **FastAPI**. It stores user meals, calculates daily nutrient totals, and provides a simple vision service for food‑image classification.

## Features
- Persistent SQLite database (`cal_ai.db`) for fast local storage.
- CRUD endpoints for meals and nutrition data.
- Integrated vision service (`vision_service.py`) using a pre‑trained Gemini/OpenAI model.
- Ready for deployment on Render, Fly.io, Koyeb, etc. via a `Procfile`.

## Quick‑Start (Windows)
```bash
python -m venv .venv
.venv\Scripts\activate   # on Unix/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Deployment
- **Render**: The repo includes a `render.yaml` and a `Procfile`. After connecting the repo, Render will automatically build and run the app with `uvicorn main:app --host 0.0.0.0 --port $PORT`.
- **Fly.io** / **Koyeb**: Use the same `Procfile` (`web: gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT`).

## License
MIT © Papito084
