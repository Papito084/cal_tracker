"""
Database layer using SQLite for user profile, meal tracking, and weight history.
"""
import sqlite3
import json
from datetime import datetime, date
from typing import Optional, Dict, Any, List
from config import settings

def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(settings.DATABASE_PATH))
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initialize database tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # User Profile table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT DEFAULT 'Usuario',
        gender TEXT NOT NULL,
        age INTEGER NOT NULL,
        height_cm REAL NOT NULL,
        current_weight_kg REAL NOT NULL,
        target_weight_kg REAL NOT NULL,
        activity_level TEXT NOT NULL,
        goal TEXT NOT NULL,
        target_weeks INTEGER NOT NULL,
        bmr REAL NOT NULL,
        tdee REAL NOT NULL,
        daily_calories REAL NOT NULL,
        protein_g REAL NOT NULL,
        fat_g REAL NOT NULL,
        carbs_g REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Daily Meals table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS daily_meals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date_logged DATE NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        meal_type TEXT DEFAULT 'Comida',
        dish_name TEXT NOT NULL,
        total_calories REAL NOT NULL,
        protein_g REAL NOT NULL,
        carbs_g REAL NOT NULL,
        fat_g REAL NOT NULL,
        fiber_g REAL DEFAULT 0.0,
        confidence_score REAL DEFAULT 1.0,
        raw_items_json TEXT,
        image_base64 TEXT
    );
    """)

    # Weight history table for charts and weight progress tracking
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS weight_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date_logged DATE NOT NULL,
        weight_kg REAL NOT NULL,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

def get_user_profile(user_id: int) -> Optional[Dict[str, Any]]:
    """Retrieve the profile for the given user_id, or None if not set."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user_profile WHERE user_id = ? ORDER BY id DESC LIMIT 1", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None
# Deprecated duplicate get_user_profile removed
# def get_user_profile() -> Optional[Dict[str, Any]]:
#     """Retrieve the latest user profile, or None if not set."""
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM user_profile ORDER BY id DESC LIMIT 1")
#     row = cursor.fetchone()
#     conn.close()
#     if row:
#         return dict(row)
#     return None

def save_user_profile(data: Dict[str, Any]) -> int:
    """Insert or update user profile and register initial weight entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO user_profile (
            user_id, name, gender, age, height_cm, current_weight_kg,
            target_weight_kg, activity_level, goal, target_weeks,
            bmr, tdee, daily_calories, protein_g, fat_g, carbs_g, updated_at
        ) VALUES (
            :user_id, :name, :gender, :age, :height_cm, :current_weight_kg,
            :target_weight_kg, :activity_level, :goal, :target_weeks,
            :bmr, :tdee, :daily_calories, :protein_g, :fat_g, :carbs_g, CURRENT_TIMESTAMP
        )
    """, data)
    profile_id = cursor.lastrowid
    
    # Also log current weight if not logged today
    today_str = date.today().isoformat()
    cursor.execute("SELECT id FROM weight_logs WHERE date_logged = ?", (today_str,))
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO weight_logs (date_logged, weight_kg, notes)
            VALUES (?, ?, 'Registro de perfil')
        """, (today_str, float(data["current_weight_kg"])))
    else:
        cursor.execute("""
            UPDATE weight_logs SET weight_kg = ? WHERE date_logged = ?
        """, (float(data["current_weight_kg"]), today_str))

    conn.commit()
    conn.close()
    return profile_id

def log_meal(
    user_id: int,
    dish_name: str,
    total_calories: float,
    protein_g: float,
    carbs_g: float,
    fat_g: float,
    fiber_g: float = 0.0,
    confidence_score: float = 1.0,
    items: Optional[List[Dict[str, Any]]] = None,
    image_base64: Optional[str] = None,
    meal_type: str = "Comida",
    target_date: Optional[str] = None
) -> int:
    """Save a logged meal."""
    if not target_date:
        target_date = date.today().isoformat()
        
    items_json = json.dumps(items) if items else "[]"

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO daily_meals (
            user_id, date_logged, meal_type, dish_name, total_calories,
            protein_g, carbs_g, fat_g, fiber_g, confidence_score,
            raw_items_json, image_base64
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        target_date, meal_type, dish_name, total_calories,
        protein_g, carbs_g, fat_g, fiber_g, confidence_score,
        items_json, image_base64
    ))
    meal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return meal_id

def update_meal(
    meal_id: int,
    dish_name: str,
    total_calories: float,
    protein_g: float,
    carbs_g: float,
    fat_g: float,
    fiber_g: float = 0.0,
    meal_type: str = "Comida"
) -> bool:
    """Update an existing meal's details."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE daily_meals
        SET dish_name = ?,
            total_calories = ?,
            protein_g = ?,
            carbs_g = ?,
            fat_g = ?,
            fiber_g = ?,
            meal_type = ?
        WHERE id = ?
    """, (
        dish_name, total_calories, protein_g, carbs_g,
        fat_g, fiber_g, meal_type, meal_id
    ))
    updated = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return updated

def get_meals_for_date(user_id: int, target_date: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieve meals for a specific date for the given user (defaults to today)."""
    if not target_date:
        target_date = date.today().isoformat()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM daily_meals
        WHERE user_id = ? AND date_logged = ?
        ORDER BY timestamp DESC
    """, (user_id, target_date))
    rows = cursor.fetchall()
    conn.close()

    meals = []
    for row in rows:
        meal = dict(row)
        try:
            meal["items"] = json.loads(meal["raw_items_json"]) if meal.get("raw_items_json") else []
        except Exception:
            meal["items"] = []
        meals.append(meal)
    return meals

def get_daily_summary(user_id: int, target_date: Optional[str] = None) -> Dict[str, float]:
    """Calculate total consumed calories and macros for a date for the given user."""
    meals = get_meals_for_date(user_id, target_date)
    summary = {
        "calories": sum(m["total_calories"] for m in meals),
        "proteins": sum(m["protein_g"] for m in meals),
        "carbs": sum(m["carbs_g"] for m in meals),
        "fats": sum(m["fat_g"] for m in meals),
        "fiber": sum(m.get("fiber_g", 0.0) for m in meals),
        "meal_count": len(meals)
    }
    return summary

def delete_meal(meal_id: int, user_id: int) -> bool:
    """Delete a meal by ID for the given user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM daily_meals WHERE id = ? AND user_id = ?", (meal_id, user_id))
    deleted = cursor.rowcount > 0
    conn.commit()
    conn.close()
    return deleted

def log_weight(weight_kg: float, target_date: Optional[str] = None, notes: str = "") -> int:
    """Log or update weight measurement for a specific date."""
    if not target_date:
        target_date = date.today().isoformat()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM weight_logs WHERE date_logged = ?", (target_date,))
    row = cursor.fetchone()
    if row:
        cursor.execute("""
            UPDATE weight_logs SET weight_kg = ?, notes = ? WHERE id = ?
        """, (weight_kg, notes, row["id"]))
        log_id = row["id"]
    else:
        cursor.execute("""
            INSERT INTO weight_logs (date_logged, weight_kg, notes)
            VALUES (?, ?, ?)
        """, (target_date, weight_kg, notes))
        log_id = cursor.lastrowid
        
    # Also update current_weight_kg in user_profile
    cursor.execute("SELECT id FROM user_profile ORDER BY id DESC LIMIT 1")
    p_row = cursor.fetchone()
    if p_row:
        cursor.execute("UPDATE user_profile SET current_weight_kg = ? WHERE id = ?", (weight_kg, p_row["id"]))

    conn.commit()
    conn.close()
    return log_id

def get_weight_history() -> List[Dict[str, Any]]:
    """Get all weight logs ordered chronologically for charts."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM weight_logs ORDER BY date_logged ASC, id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def clear_all_data() -> None:
    """Utility to reset database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM daily_meals")
    cursor.execute("DELETE FROM user_profile")
    cursor.execute("DELETE FROM weight_logs")
    conn.commit()
    conn.close()
