"""
Shopping list generation and optimization for wochenplan.net.

Combines ingredients from all recipes in a meal plan:
- Aggregates same ingredients (sums quantities)
- Scales by person count
- Groups by store section (category)
- Filters out staple items (salt, pepper, oil) that most households have
"""

from models import (
    get_meal_plan_with_recipes, get_recipe_with_ingredients,
    create_shopping_list, add_shopping_list_item
)

# Display names for categories (store sections)
CATEGORY_LABELS = {
    "gemuese": "Obst & Gemüse",
    "obst": "Obst & Gemüse",
    "protein": "Fleisch & Fisch",
    "milch": "Milchprodukte",
    "getreide": "Brot & Backwaren / Teigwaren",
    "konserve": "Konserven & Saucen",
    "gewuerz": "Gewürze & Kräuter",
    "sonstiges": "Sonstiges",
}

# Display order for categories
CATEGORY_ORDER = [
    "gemuese", "obst", "protein", "milch",
    "getreide", "konserve", "gewuerz", "sonstiges"
]


def generate_shopping_list(conn, plan_id):
    """
    Generate an optimized shopping list from a meal plan.

    Returns: shopping_list_id
    """
    plan = get_meal_plan_with_recipes(conn, plan_id)
    persons = plan["persons"]

    # Collect all ingredients with quantities
    ingredient_totals = {}  # ingredient_id -> {name, quantity, unit, category, is_staple}

    for entry in plan["entries"]:
        recipe = get_recipe_with_ingredients(conn, entry["recipe_id"])
        scale = persons / recipe["base_servings"]

        for ing in recipe["ingredients"]:
            ing_id = ing["ingredient_id"]
            scaled_qty = ing["quantity"] * scale

            if ing_id in ingredient_totals:
                ingredient_totals[ing_id]["quantity"] += scaled_qty
            else:
                ingredient_totals[ing_id] = {
                    "ingredient_id": ing_id,
                    "name": ing["ingredient_name"],
                    "quantity": scaled_qty,
                    "unit": ing["unit"],
                    "category": ing["category"],
                    "is_staple": ing.get("ingredient_cost", "mittel"),
                }

    # Create shopping list in DB
    list_id = create_shopping_list(conn, plan_id)

    for ing_id, data in ingredient_totals.items():
        add_shopping_list_item(
            conn, list_id, ing_id,
            round_quantity(data["quantity"], data["unit"]),
            data["unit"]
        )

    return list_id


def round_quantity(qty, unit):
    """Round quantities to practical shopping amounts."""
    # Whole items
    if unit in ("Stück", "Dose", "Becher", "Glas", "Bund"):
        import math
        return math.ceil(qty)

    # Weights - round to nearest 50g
    if unit == "g":
        return round(qty / 50) * 50 or 50

    # Volumes - round to nearest 50ml
    if unit == "ml":
        return round(qty / 50) * 50 or 50

    # Spoons and pinches - round up
    if unit in ("EL", "TL", "Prise", "Zehe"):
        import math
        return math.ceil(qty)

    return round(qty, 1)


def get_grouped_shopping_list(conn, list_id):
    """
    Get shopping list items grouped by store section.

    Returns: dict of category_label -> list of items
    """
    from models import get_shopping_list
    items = get_shopping_list(conn, list_id)

    grouped = {}
    for item in items:
        cat = item["category"]
        label = CATEGORY_LABELS.get(cat, "Sonstiges")

        if label not in grouped:
            grouped[label] = []
        grouped[label].append(item)

    # Sort by category order
    ordered = {}
    for cat in CATEGORY_ORDER:
        label = CATEGORY_LABELS.get(cat, "Sonstiges")
        if label in grouped and label not in ordered:
            ordered[label] = grouped[label]

    return ordered


def get_staple_items(conn, list_id):
    """Get items that are staple/pantry items (likely already at home)."""
    from models import get_shopping_list
    items = get_shopping_list(conn, list_id)
    return [i for i in items if i["is_staple"]]


def get_fresh_items(conn, list_id):
    """Get items that need to be purchased fresh."""
    from models import get_shopping_list
    items = get_shopping_list(conn, list_id)
    return [i for i in items if not i["is_staple"]]
