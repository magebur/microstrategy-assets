"""
Data models for wochenplan.net meal planning system.
Uses SQLite for persistence with a simple ORM-like layer.
"""

import sqlite3
import json
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "wochenplan.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_db()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS ingredient (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            category TEXT NOT NULL,
            unit TEXT NOT NULL DEFAULT 'g',
            cost_level TEXT NOT NULL DEFAULT 'mittel',
            is_staple INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS recipe (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            base_servings INTEGER NOT NULL DEFAULT 2,
            prep_time_minutes INTEGER NOT NULL DEFAULT 15,
            cook_time_minutes INTEGER NOT NULL DEFAULT 20,
            difficulty TEXT NOT NULL DEFAULT 'einfach',
            is_vegetarian INTEGER NOT NULL DEFAULT 0,
            is_kid_friendly INTEGER NOT NULL DEFAULT 0,
            is_quick INTEGER NOT NULL DEFAULT 0,
            cost_level TEXT NOT NULL DEFAULT 'mittel',
            tags TEXT NOT NULL DEFAULT '[]'
        );

        CREATE TABLE IF NOT EXISTS recipe_ingredient (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            is_optional INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (recipe_id) REFERENCES recipe(id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredient(id)
        );

        CREATE TABLE IF NOT EXISTS meal_plan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            persons INTEGER NOT NULL DEFAULT 2,
            meals_per_week INTEGER NOT NULL DEFAULT 5,
            preferences TEXT NOT NULL DEFAULT '{}',
            savings_mode INTEGER NOT NULL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS meal_plan_entry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_plan_id INTEGER NOT NULL,
            day_index INTEGER NOT NULL,
            day_label TEXT NOT NULL,
            recipe_id INTEGER NOT NULL,
            FOREIGN KEY (meal_plan_id) REFERENCES meal_plan(id),
            FOREIGN KEY (recipe_id) REFERENCES recipe(id)
        );

        CREATE TABLE IF NOT EXISTS shopping_list (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            meal_plan_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (meal_plan_id) REFERENCES meal_plan(id)
        );

        CREATE TABLE IF NOT EXISTS shopping_list_item (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            shopping_list_id INTEGER NOT NULL,
            ingredient_id INTEGER NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            is_checked INTEGER NOT NULL DEFAULT 0,
            FOREIGN KEY (shopping_list_id) REFERENCES shopping_list(id),
            FOREIGN KEY (ingredient_id) REFERENCES ingredient(id)
        );
    """)
    conn.commit()
    conn.close()


def get_all_recipes(conn):
    rows = conn.execute("SELECT * FROM recipe").fetchall()
    return [dict(r) for r in rows]


def get_recipe_with_ingredients(conn, recipe_id):
    recipe = dict(conn.execute(
        "SELECT * FROM recipe WHERE id = ?", (recipe_id,)
    ).fetchone())
    ingredients = conn.execute("""
        SELECT ri.*, i.name as ingredient_name, i.category, i.cost_level as ingredient_cost
        FROM recipe_ingredient ri
        JOIN ingredient i ON ri.ingredient_id = i.id
        WHERE ri.recipe_id = ?
    """, (recipe_id,)).fetchall()
    recipe["ingredients"] = [dict(i) for i in ingredients]
    return recipe


def get_ingredient_ids_for_recipe(conn, recipe_id):
    rows = conn.execute(
        "SELECT ingredient_id FROM recipe_ingredient WHERE recipe_id = ?",
        (recipe_id,)
    ).fetchall()
    return {r["ingredient_id"] for r in rows}


def create_meal_plan(conn, persons, meals_per_week, preferences, savings_mode):
    cursor = conn.execute(
        "INSERT INTO meal_plan (persons, meals_per_week, preferences, savings_mode) VALUES (?, ?, ?, ?)",
        (persons, meals_per_week, json.dumps(preferences), int(savings_mode))
    )
    conn.commit()
    return cursor.lastrowid


def add_meal_plan_entry(conn, plan_id, day_index, day_label, recipe_id):
    conn.execute(
        "INSERT INTO meal_plan_entry (meal_plan_id, day_index, day_label, recipe_id) VALUES (?, ?, ?, ?)",
        (plan_id, day_index, day_label, recipe_id)
    )
    conn.commit()


def get_meal_plan_with_recipes(conn, plan_id):
    plan = dict(conn.execute(
        "SELECT * FROM meal_plan WHERE id = ?", (plan_id,)
    ).fetchone())
    entries = conn.execute("""
        SELECT mpe.*, r.name as recipe_name, r.description, r.prep_time_minutes,
               r.cook_time_minutes, r.difficulty, r.is_vegetarian, r.is_kid_friendly,
               r.is_quick, r.cost_level
        FROM meal_plan_entry mpe
        JOIN recipe r ON mpe.recipe_id = r.id
        WHERE mpe.meal_plan_id = ?
        ORDER BY mpe.day_index
    """, (plan_id,)).fetchall()
    plan["entries"] = [dict(e) for e in entries]
    return plan


def create_shopping_list(conn, plan_id):
    cursor = conn.execute(
        "INSERT INTO shopping_list (meal_plan_id) VALUES (?)",
        (plan_id,)
    )
    conn.commit()
    return cursor.lastrowid


def add_shopping_list_item(conn, list_id, ingredient_id, quantity, unit):
    conn.execute(
        "INSERT INTO shopping_list_item (shopping_list_id, ingredient_id, quantity, unit) VALUES (?, ?, ?, ?)",
        (list_id, ingredient_id, quantity, unit)
    )
    conn.commit()


def get_shopping_list(conn, list_id):
    items = conn.execute("""
        SELECT sli.*, i.name as ingredient_name, i.category, i.is_staple
        FROM shopping_list_item sli
        JOIN ingredient i ON sli.ingredient_id = i.id
        WHERE sli.shopping_list_id = ?
        ORDER BY i.category, i.name
    """, (list_id,)).fetchall()
    return [dict(i) for i in items]


def toggle_shopping_item(conn, item_id, checked):
    conn.execute(
        "UPDATE shopping_list_item SET is_checked = ? WHERE id = ?",
        (int(checked), item_id)
    )
    conn.commit()
