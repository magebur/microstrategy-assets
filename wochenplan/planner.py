"""
Meal plan generation engine for wochenplan.net.

Core algorithm:
1. Filter recipes by user preferences (vegetarian, kid-friendly, quick, savings)
2. Select first recipe randomly from filtered pool
3. Greedily pick subsequent recipes maximizing ingredient overlap with already-selected recipes
4. Apply variety constraints (no duplicate protein types, mix of cooking methods)
5. Return ordered plan for the week

Design principle: "Küchenlogik statt Ernährungswissenschaft"
- No calories, no macros
- Maximize ingredient reuse to minimize shopping
- Ensure basic variety (not all pasta, not all rice)
"""

import random
from collections import Counter
from models import (
    get_all_recipes, get_ingredient_ids_for_recipe,
    create_meal_plan, add_meal_plan_entry, get_recipe_with_ingredients
)

DAY_LABELS = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]


def filter_recipes(recipes, preferences):
    """Filter recipe pool by user preferences."""
    filtered = list(recipes)

    if preferences.get("vegetarian"):
        filtered = [r for r in filtered if r["is_vegetarian"]]

    if preferences.get("kid_friendly"):
        filtered = [r for r in filtered if r["is_kid_friendly"]]

    if preferences.get("quick"):
        filtered = [r for r in filtered if r["is_quick"]]

    return filtered


def apply_savings_filter(recipes):
    """In savings mode, prefer cheaper recipes and limit expensive ones."""
    cheap = [r for r in recipes if r["cost_level"] == "guenstig"]
    medium = [r for r in recipes if r["cost_level"] == "mittel"]
    # Exclude 'teuer' recipes entirely in savings mode
    return cheap + medium


def compute_overlap_score(conn, candidate_id, selected_ids):
    """Score a candidate recipe by how many ingredients it shares with already selected recipes."""
    if not selected_ids:
        return 0

    candidate_ingredients = get_ingredient_ids_for_recipe(conn, candidate_id)
    selected_ingredients = set()
    for rid in selected_ids:
        selected_ingredients.update(get_ingredient_ids_for_recipe(conn, rid))

    overlap = candidate_ingredients & selected_ingredients
    return len(overlap)


def get_recipe_tags(recipe):
    """Extract tags from recipe for variety checking."""
    tags = recipe.get("tags", "[]")
    if isinstance(tags, str):
        # Parse the string representation of list
        tags = tags.strip("[]").replace("'", "").replace('"', "").split(", ")
    return [t.strip() for t in tags if t.strip()]


def check_variety(candidate, selected_recipes):
    """Ensure we don't pick too many recipes of the same type."""
    if not selected_recipes:
        return True

    candidate_tags = set(get_recipe_tags(candidate))
    tag_counts = Counter()
    for r in selected_recipes:
        for t in get_recipe_tags(r):
            tag_counts[t] += 1

    # Don't allow more than 2 pasta dishes
    if "pasta" in candidate_tags and tag_counts.get("pasta", 0) >= 2:
        return False

    # Don't allow more than 2 rice dishes
    if "reis" in candidate_tags and tag_counts.get("reis", 0) >= 2:
        return False

    # Don't allow more than 2 of the same protein source
    protein_tags = {"hackfleisch", "haehnchen", "pute", "fisch", "eier", "tofu"}
    for pt in protein_tags:
        if pt in candidate_tags and tag_counts.get(pt, 0) >= 2:
            return False

    return True


def generate_plan(conn, persons, meals_per_week, preferences, savings_mode=False):
    """
    Generate a weekly meal plan.

    Returns: meal_plan_id
    """
    all_recipes = get_all_recipes(conn)
    pool = filter_recipes(all_recipes, preferences)

    if savings_mode:
        pool = apply_savings_filter(pool)

    if len(pool) < meals_per_week:
        # Fall back to all recipes if not enough match preferences
        pool = all_recipes
        if savings_mode:
            pool = apply_savings_filter(pool)

    # Create the plan in DB
    plan_id = create_meal_plan(conn, persons, meals_per_week, preferences, savings_mode)

    selected = []
    selected_ids = []
    remaining_pool = list(pool)

    for i in range(meals_per_week):
        if not remaining_pool:
            # Re-use the pool if we run out (shouldn't happen with 30 recipes)
            remaining_pool = [r for r in pool if r["id"] not in selected_ids]
            if not remaining_pool:
                remaining_pool = list(pool)

        if i == 0:
            # First recipe: pick randomly
            candidate = random.choice(remaining_pool)
        else:
            # Score all remaining candidates by ingredient overlap + variety
            scored = []
            for r in remaining_pool:
                if r["id"] in selected_ids:
                    continue
                if not check_variety(r, selected):
                    continue
                overlap = compute_overlap_score(conn, r["id"], selected_ids)
                scored.append((r, overlap))

            if not scored:
                # Fallback: if variety constraints are too strict, relax them
                for r in remaining_pool:
                    if r["id"] not in selected_ids:
                        overlap = compute_overlap_score(conn, r["id"], selected_ids)
                        scored.append((r, overlap))

            if not scored:
                break

            # Sort by overlap score descending, pick from top 3 randomly for variety
            scored.sort(key=lambda x: x[1], reverse=True)
            top_n = min(3, len(scored))
            # Weight towards higher overlap
            weights = [3, 2, 1][:top_n]
            candidate = random.choices([s[0] for s in scored[:top_n]], weights=weights, k=1)[0]

        selected.append(candidate)
        selected_ids.append(candidate["id"])
        remaining_pool = [r for r in remaining_pool if r["id"] != candidate["id"]]

        day_label = DAY_LABELS[i % 7]
        add_meal_plan_entry(conn, plan_id, i, day_label, candidate["id"])

    return plan_id


def swap_recipe(conn, plan_id, day_index, current_recipe_id, preferences, savings_mode=False):
    """Swap a single recipe in the plan, maintaining overlap with neighbors."""
    all_recipes = get_all_recipes(conn)
    pool = filter_recipes(all_recipes, preferences)
    if savings_mode:
        pool = apply_savings_filter(pool)

    # Get other recipe IDs in this plan
    from models import get_meal_plan_with_recipes
    plan = get_meal_plan_with_recipes(conn, plan_id)
    other_ids = [e["recipe_id"] for e in plan["entries"] if e["day_index"] != day_index]

    # Find best replacement
    scored = []
    for r in pool:
        if r["id"] == current_recipe_id:
            continue
        if r["id"] in other_ids:
            continue
        overlap = compute_overlap_score(conn, r["id"], other_ids)
        scored.append((r, overlap))

    if not scored:
        return None

    scored.sort(key=lambda x: x[1], reverse=True)
    top_n = min(3, len(scored))
    chosen = random.choices([s[0] for s in scored[:top_n]], weights=[3, 2, 1][:top_n], k=1)[0]

    # Update the entry
    conn.execute(
        "UPDATE meal_plan_entry SET recipe_id = ? WHERE meal_plan_id = ? AND day_index = ?",
        (chosen["id"], plan_id, day_index)
    )
    conn.commit()

    return chosen["id"]
