"""
wochenplan.net - Flask Web Application

Weekly meal planning tool for families and working professionals.
"HelloFresh ohne Box, ohne Verpackung, ohne Aufpreis."

User Flow:
1. / - Enter preferences (persons, meals, dietary, savings mode)
2. /plan/<id> - View generated weekly meal plan, swap recipes
3. /shopping/<plan_id> - View optimized shopping list
4. /check/<list_id> - Pantry check: mark items already at home
"""

import json
from flask import Flask, render_template, request, redirect, url_for, jsonify
from models import (
    init_db, get_db, get_meal_plan_with_recipes,
    get_recipe_with_ingredients, toggle_shopping_item
)
from recipes_data import seed_database
from planner import generate_plan, swap_recipe
from shopping import generate_shopping_list, get_grouped_shopping_list

app = Flask(__name__)


@app.before_request
def ensure_db():
    """Initialize and seed database on first request."""
    conn = get_db()
    init_db()
    seed_database(conn)
    conn.close()


@app.route("/")
def index():
    """Landing page with preference input form."""
    return render_template("index.html")


@app.route("/generate", methods=["POST"])
def generate():
    """Generate a meal plan from user preferences."""
    persons = int(request.form.get("persons", 2))
    meals_per_week = int(request.form.get("meals_per_week", 5))
    vegetarian = request.form.get("vegetarian") == "on"
    kid_friendly = request.form.get("kid_friendly") == "on"
    quick = request.form.get("quick") == "on"
    savings_mode = request.form.get("savings_mode") == "on"

    preferences = {
        "vegetarian": vegetarian,
        "kid_friendly": kid_friendly,
        "quick": quick,
    }

    conn = get_db()
    plan_id = generate_plan(conn, persons, meals_per_week, preferences, savings_mode)
    conn.close()

    return redirect(url_for("plan", plan_id=plan_id))


@app.route("/plan/<int:plan_id>")
def plan(plan_id):
    """Display the generated weekly meal plan."""
    conn = get_db()
    plan_data = get_meal_plan_with_recipes(conn, plan_id)

    # Get full recipe details for each entry
    for entry in plan_data["entries"]:
        recipe = get_recipe_with_ingredients(conn, entry["recipe_id"])
        entry["recipe_detail"] = recipe

    conn.close()
    return render_template("plan.html", plan=plan_data)


@app.route("/swap", methods=["POST"])
def swap():
    """Swap a recipe in the meal plan via AJAX."""
    data = request.get_json()
    plan_id = data["plan_id"]
    day_index = data["day_index"]
    current_recipe_id = data["current_recipe_id"]

    conn = get_db()
    plan_data = get_meal_plan_with_recipes(conn, plan_id)
    preferences = json.loads(plan_data["preferences"])
    savings_mode = bool(plan_data["savings_mode"])

    new_recipe_id = swap_recipe(conn, plan_id, day_index, current_recipe_id, preferences, savings_mode)

    if new_recipe_id:
        recipe = get_recipe_with_ingredients(conn, new_recipe_id)
        conn.close()
        return jsonify({
            "success": True,
            "recipe": {
                "id": recipe["id"],
                "name": recipe["name"],
                "description": recipe["description"],
                "prep_time_minutes": recipe["prep_time_minutes"],
                "cook_time_minutes": recipe["cook_time_minutes"],
                "difficulty": recipe["difficulty"],
                "is_vegetarian": recipe["is_vegetarian"],
                "is_quick": recipe["is_quick"],
                "cost_level": recipe["cost_level"],
                "ingredients": [
                    {"name": i["ingredient_name"], "quantity": i["quantity"], "unit": i["unit"]}
                    for i in recipe["ingredients"]
                ]
            }
        })
    conn.close()
    return jsonify({"success": False})


@app.route("/shopping/<int:plan_id>")
def shopping(plan_id):
    """Generate and display the shopping list."""
    conn = get_db()
    list_id = generate_shopping_list(conn, plan_id)
    grouped = get_grouped_shopping_list(conn, list_id)
    plan_data = get_meal_plan_with_recipes(conn, plan_id)
    conn.close()

    return render_template("shopping.html", grouped=grouped, list_id=list_id,
                           plan_id=plan_id, plan=plan_data)


@app.route("/check/<int:list_id>")
def check(list_id):
    """Pantry check view - mark items already at home."""
    conn = get_db()
    grouped = get_grouped_shopping_list(conn, list_id)

    # Get plan_id from shopping list
    row = conn.execute(
        "SELECT meal_plan_id FROM shopping_list WHERE id = ?", (list_id,)
    ).fetchone()
    plan_id = row["meal_plan_id"] if row else None

    conn.close()
    return render_template("check.html", grouped=grouped, list_id=list_id, plan_id=plan_id)


@app.route("/toggle_item", methods=["POST"])
def toggle_item():
    """Toggle a shopping list item checked state via AJAX."""
    data = request.get_json()
    item_id = data["item_id"]
    checked = data["checked"]

    conn = get_db()
    toggle_shopping_item(conn, item_id, checked)
    conn.close()

    return jsonify({"success": True})


@app.route("/recipe/<int:recipe_id>")
def recipe_detail(recipe_id):
    """View a single recipe detail."""
    conn = get_db()
    recipe = get_recipe_with_ingredients(conn, recipe_id)
    conn.close()
    return render_template("recipe.html", recipe=recipe)


if __name__ == "__main__":
    init_db()
    conn = get_db()
    seed_database(conn)
    conn.close()
    app.run(debug=True, host="0.0.0.0", port=5000)
