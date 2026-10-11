# Cal Tracker

Cal Tracker is a lightweight Calorie & Nutrition tracking API built with FastAPI. It stores user meals, calculates daily nutrient totals, and offers a simple vision service for food image classification.

## Features
- Persistent SQLite DB (cal_ai.db) for fast local storage.
- Endpoints for CRUD operations on meals and nutrition data.
- Integrated vision service (ision_service.py) using a pre‑trained model.
- Ready for deployment on Fly.io / Render via Procfile.

## Quick‑Start
`ash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
`

## License
MIT © Papito084
