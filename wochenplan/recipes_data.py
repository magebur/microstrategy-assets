"""
Seed data for wochenplan.net recipe database.

Design principle: Recipes share ingredients intentionally to minimize
shopping lists and reduce food waste (HelloFresh logic without the box).

Categories for ingredients:
  gemuese, obst, protein, milch, getreide, konserve, gewuerz, sonstiges

Cost levels: guenstig, mittel, teuer
"""

INGREDIENTS = [
    # Gemüse
    {"name": "Zwiebeln", "category": "gemuese", "unit": "Stück", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Knoblauch", "category": "gemuese", "unit": "Zehe", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Kartoffeln", "category": "gemuese", "unit": "g", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Karotten", "category": "gemuese", "unit": "Stück", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Tomaten", "category": "gemuese", "unit": "Stück", "cost_level": "mittel", "is_staple": 0},
    {"name": "Paprika", "category": "gemuese", "unit": "Stück", "cost_level": "mittel", "is_staple": 0},
    {"name": "Zucchini", "category": "gemuese", "unit": "Stück", "cost_level": "mittel", "is_staple": 0},
    {"name": "Brokkoli", "category": "gemuese", "unit": "Stück", "cost_level": "mittel", "is_staple": 0},
    {"name": "Spinat (frisch)", "category": "gemuese", "unit": "g", "cost_level": "mittel", "is_staple": 0},
    {"name": "Champignons", "category": "gemuese", "unit": "g", "cost_level": "mittel", "is_staple": 0},
    {"name": "Lauch", "category": "gemuese", "unit": "Stück", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Eisbergsalat", "category": "gemuese", "unit": "Stück", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Gurke", "category": "gemuese", "unit": "Stück", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Mais (Dose)", "category": "konserve", "unit": "Dose", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Kidneybohnen (Dose)", "category": "konserve", "unit": "Dose", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Süßkartoffel", "category": "gemuese", "unit": "Stück", "cost_level": "mittel", "is_staple": 0},
    {"name": "Tiefkühl-Erbsen", "category": "gemuese", "unit": "g", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Frühlingszwiebeln", "category": "gemuese", "unit": "Bund", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Ingwer", "category": "gemuese", "unit": "Stück", "cost_level": "guenstig", "is_staple": 0},

    # Proteine
    {"name": "Hähnchenbrust", "category": "protein", "unit": "g", "cost_level": "mittel", "is_staple": 0},
    {"name": "Hackfleisch (gemischt)", "category": "protein", "unit": "g", "cost_level": "mittel", "is_staple": 0},
    {"name": "Lachs-Filet", "category": "protein", "unit": "g", "cost_level": "teuer", "is_staple": 0},
    {"name": "Würstchen", "category": "protein", "unit": "Stück", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Speck / Schinken", "category": "protein", "unit": "g", "cost_level": "mittel", "is_staple": 0},
    {"name": "Eier", "category": "protein", "unit": "Stück", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Tofu", "category": "protein", "unit": "g", "cost_level": "mittel", "is_staple": 0},
    {"name": "Rinderhüftsteak", "category": "protein", "unit": "g", "cost_level": "teuer", "is_staple": 0},
    {"name": "Thunfisch (Dose)", "category": "konserve", "unit": "Dose", "cost_level": "mittel", "is_staple": 0},
    {"name": "Bratwurst", "category": "protein", "unit": "Stück", "cost_level": "mittel", "is_staple": 0},
    {"name": "Putengeschnetzeltes", "category": "protein", "unit": "g", "cost_level": "mittel", "is_staple": 0},

    # Milchprodukte
    {"name": "Butter", "category": "milch", "unit": "g", "cost_level": "mittel", "is_staple": 1},
    {"name": "Milch", "category": "milch", "unit": "ml", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Sahne", "category": "milch", "unit": "ml", "cost_level": "mittel", "is_staple": 0},
    {"name": "Schmand", "category": "milch", "unit": "Becher", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Geriebener Käse", "category": "milch", "unit": "g", "cost_level": "mittel", "is_staple": 0},
    {"name": "Frischkäse", "category": "milch", "unit": "g", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Mozzarella", "category": "milch", "unit": "Stück", "cost_level": "mittel", "is_staple": 0},
    {"name": "Parmesan", "category": "milch", "unit": "g", "cost_level": "mittel", "is_staple": 0},
    {"name": "Joghurt (natur)", "category": "milch", "unit": "Becher", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Feta", "category": "milch", "unit": "g", "cost_level": "mittel", "is_staple": 0},
    {"name": "Crème fraîche", "category": "milch", "unit": "Becher", "cost_level": "guenstig", "is_staple": 0},

    # Getreide & Teigwaren
    {"name": "Spaghetti", "category": "getreide", "unit": "g", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Penne", "category": "getreide", "unit": "g", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Reis", "category": "getreide", "unit": "g", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Brot / Brötchen", "category": "getreide", "unit": "Stück", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Tortilla-Wraps", "category": "getreide", "unit": "Stück", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Mehl", "category": "getreide", "unit": "g", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Pizzateig (fertig)", "category": "getreide", "unit": "Stück", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Lasagne-Platten", "category": "getreide", "unit": "g", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Couscous", "category": "getreide", "unit": "g", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Kartoffelpüree-Flocken", "category": "getreide", "unit": "g", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Asia-Nudeln", "category": "getreide", "unit": "g", "cost_level": "guenstig", "is_staple": 0},

    # Konserven & Saucen
    {"name": "Passierte Tomaten", "category": "konserve", "unit": "ml", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Tomatenmark", "category": "konserve", "unit": "EL", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Kokosmilch", "category": "konserve", "unit": "Dose", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Gemüsebrühe", "category": "konserve", "unit": "ml", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Sojasauce", "category": "konserve", "unit": "EL", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Senf", "category": "konserve", "unit": "EL", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Ketchup", "category": "konserve", "unit": "EL", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Olivenöl", "category": "konserve", "unit": "EL", "cost_level": "mittel", "is_staple": 1},
    {"name": "Sonnenblumenöl", "category": "konserve", "unit": "EL", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Essig", "category": "konserve", "unit": "EL", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Currypaste", "category": "konserve", "unit": "EL", "cost_level": "mittel", "is_staple": 0},
    {"name": "Pesto", "category": "konserve", "unit": "Glas", "cost_level": "mittel", "is_staple": 0},

    # Gewürze
    {"name": "Salz", "category": "gewuerz", "unit": "Prise", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Pfeffer", "category": "gewuerz", "unit": "Prise", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Paprikapulver", "category": "gewuerz", "unit": "TL", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Kreuzkümmel", "category": "gewuerz", "unit": "TL", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Currypulver", "category": "gewuerz", "unit": "TL", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Oregano (getr.)", "category": "gewuerz", "unit": "TL", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Basilikum (frisch)", "category": "gewuerz", "unit": "Bund", "cost_level": "mittel", "is_staple": 0},
    {"name": "Petersilie", "category": "gewuerz", "unit": "Bund", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Zitrone", "category": "obst", "unit": "Stück", "cost_level": "guenstig", "is_staple": 0},
    {"name": "Zucker", "category": "gewuerz", "unit": "EL", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Muskatnuss", "category": "gewuerz", "unit": "Prise", "cost_level": "guenstig", "is_staple": 1},
    {"name": "Chiliflocken", "category": "gewuerz", "unit": "Prise", "cost_level": "guenstig", "is_staple": 1},
]

# Recipes designed with intentional ingredient overlap
# Groups that share ingredients:
#   - Tomaten-Gruppe: Bolognese, Chili, Pizza, Shakshuka
#   - Kartoffel-Gruppe: Kartoffelsuppe, Bauernpfanne, Ofenkartoffeln
#   - Hähnchen-Gruppe: Hähnchen-Reis, Wraps, Geschnetzeltes
#   - Pasta-Gruppe: Bolognese, Carbonara, Pesto-Pasta, Lasagne
#   - Asia-Gruppe: Gebratener Reis, Curry, Nudelpfanne

RECIPES = [
    # === PASTA-GRUPPE ===
    {
        "name": "Spaghetti Bolognese",
        "description": "Der Klassiker für die ganze Familie. Deftige Hackfleischsauce mit Spaghetti.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 25,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["pasta", "klassiker", "hackfleisch"],
        "ingredients": [
            ("Spaghetti", 500, "g"),
            ("Hackfleisch (gemischt)", 400, "g"),
            ("Zwiebeln", 1, "Stück"),
            ("Knoblauch", 2, "Zehe"),
            ("Karotten", 2, "Stück"),
            ("Passierte Tomaten", 500, "ml"),
            ("Tomatenmark", 2, "EL"),
            ("Olivenöl", 2, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Oregano (getr.)", 1, "TL"),
            ("Parmesan", 40, "g"),
        ]
    },
    {
        "name": "Penne mit Pesto und Tomaten",
        "description": "Schnelle Pasta mit grünem Pesto, frischen Tomaten und Parmesan.",
        "base_servings": 4, "prep_time_minutes": 5, "cook_time_minutes": 12,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["pasta", "schnell", "vegetarisch"],
        "ingredients": [
            ("Penne", 500, "g"),
            ("Pesto", 1, "Glas"),
            ("Tomaten", 3, "Stück"),
            ("Parmesan", 40, "g"),
            ("Olivenöl", 1, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
        ]
    },
    {
        "name": "Pasta Carbonara",
        "description": "Cremige Carbonara mit Speck und Ei – authentisch und schnell.",
        "base_servings": 4, "prep_time_minutes": 5, "cook_time_minutes": 15,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["pasta", "schnell", "klassiker"],
        "ingredients": [
            ("Spaghetti", 500, "g"),
            ("Speck / Schinken", 150, "g"),
            ("Eier", 4, "Stück"),
            ("Parmesan", 60, "g"),
            ("Knoblauch", 1, "Zehe"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
        ]
    },
    {
        "name": "Lasagne",
        "description": "Schichtweise Lasagne mit Hackfleisch-Ragout und Béchamel.",
        "base_servings": 4, "prep_time_minutes": 20, "cook_time_minutes": 40,
        "difficulty": "mittel", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 0,
        "cost_level": "mittel",
        "tags": ["pasta", "ofen", "hackfleisch"],
        "ingredients": [
            ("Lasagne-Platten", 250, "g"),
            ("Hackfleisch (gemischt)", 500, "g"),
            ("Zwiebeln", 1, "Stück"),
            ("Knoblauch", 2, "Zehe"),
            ("Passierte Tomaten", 500, "ml"),
            ("Tomatenmark", 2, "EL"),
            ("Butter", 40, "g"),
            ("Mehl", 40, "g"),
            ("Milch", 500, "ml"),
            ("Geriebener Käse", 150, "g"),
            ("Muskatnuss", 1, "Prise"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Olivenöl", 1, "EL"),
        ]
    },
    {
        "name": "One-Pot Nudeln mit Gemüse",
        "description": "Alles in einem Topf: Nudeln, Zucchini, Paprika und cremige Tomatensauce.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 20,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["pasta", "vegetarisch", "one-pot"],
        "ingredients": [
            ("Penne", 400, "g"),
            ("Zucchini", 1, "Stück"),
            ("Paprika", 1, "Stück"),
            ("Passierte Tomaten", 400, "ml"),
            ("Sahne", 100, "ml"),
            ("Zwiebeln", 1, "Stück"),
            ("Knoblauch", 2, "Zehe"),
            ("Geriebener Käse", 80, "g"),
            ("Olivenöl", 2, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Oregano (getr.)", 1, "TL"),
        ]
    },

    # === KARTOFFEL-GRUPPE ===
    {
        "name": "Kartoffelsuppe mit Würstchen",
        "description": "Sättigende Kartoffelsuppe – cremig, deftig und schnell gemacht.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 25,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["suppe", "kartoffel", "deftig"],
        "ingredients": [
            ("Kartoffeln", 800, "g"),
            ("Würstchen", 4, "Stück"),
            ("Zwiebeln", 1, "Stück"),
            ("Lauch", 1, "Stück"),
            ("Karotten", 2, "Stück"),
            ("Gemüsebrühe", 800, "ml"),
            ("Sahne", 100, "ml"),
            ("Butter", 20, "g"),
            ("Muskatnuss", 1, "Prise"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Petersilie", 0.5, "Bund"),
        ]
    },
    {
        "name": "Bauernpfanne",
        "description": "Herzhafte Pfanne mit Kartoffeln, Paprika, Speck und Ei.",
        "base_servings": 4, "prep_time_minutes": 15, "cook_time_minutes": 20,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["pfanne", "kartoffel", "deftig"],
        "ingredients": [
            ("Kartoffeln", 600, "g"),
            ("Paprika", 2, "Stück"),
            ("Zwiebeln", 1, "Stück"),
            ("Speck / Schinken", 150, "g"),
            ("Eier", 4, "Stück"),
            ("Geriebener Käse", 80, "g"),
            ("Sonnenblumenöl", 2, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Paprikapulver", 1, "TL"),
        ]
    },
    {
        "name": "Ofenkartoffeln mit Kräuterquark",
        "description": "Knusprige Ofenkartoffeln mit cremigem Kräuterquark und Salat.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 40,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 1, "is_quick": 0,
        "cost_level": "guenstig",
        "tags": ["ofen", "kartoffel", "vegetarisch"],
        "ingredients": [
            ("Kartoffeln", 800, "g"),
            ("Joghurt (natur)", 1, "Becher"),
            ("Frischkäse", 100, "g"),
            ("Gurke", 0.5, "Stück"),
            ("Petersilie", 0.5, "Bund"),
            ("Olivenöl", 3, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
        ]
    },

    # === HÄHNCHEN-GRUPPE ===
    {
        "name": "Hähnchen-Reis-Pfanne",
        "description": "Gebratenes Hähnchen mit Reis, Paprika und Erbsen.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 20,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "mittel",
        "tags": ["reis", "haehnchen", "pfanne"],
        "ingredients": [
            ("Hähnchenbrust", 500, "g"),
            ("Reis", 300, "g"),
            ("Paprika", 1, "Stück"),
            ("Tiefkühl-Erbsen", 150, "g"),
            ("Zwiebeln", 1, "Stück"),
            ("Knoblauch", 1, "Zehe"),
            ("Sojasauce", 2, "EL"),
            ("Sonnenblumenöl", 2, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Currypulver", 1, "TL"),
        ]
    },
    {
        "name": "Hähnchen-Wraps",
        "description": "Gefüllte Tortillas mit Hähnchen, Salat, Tomaten und Joghurt-Dip.",
        "base_servings": 4, "prep_time_minutes": 15, "cook_time_minutes": 10,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "mittel",
        "tags": ["wraps", "haehnchen", "schnell"],
        "ingredients": [
            ("Hähnchenbrust", 400, "g"),
            ("Tortilla-Wraps", 4, "Stück"),
            ("Eisbergsalat", 0.5, "Stück"),
            ("Tomaten", 2, "Stück"),
            ("Gurke", 0.5, "Stück"),
            ("Joghurt (natur)", 1, "Becher"),
            ("Paprikapulver", 1, "TL"),
            ("Kreuzkümmel", 0.5, "TL"),
            ("Sonnenblumenöl", 1, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Zitrone", 0.5, "Stück"),
        ]
    },
    {
        "name": "Putengeschnetzeltes mit Champignons",
        "description": "Cremiges Geschnetzeltes mit Champignons und Reis.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 20,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "mittel",
        "tags": ["reis", "pute", "cremig"],
        "ingredients": [
            ("Putengeschnetzeltes", 500, "g"),
            ("Champignons", 250, "g"),
            ("Reis", 300, "g"),
            ("Sahne", 200, "ml"),
            ("Zwiebeln", 1, "Stück"),
            ("Knoblauch", 1, "Zehe"),
            ("Butter", 20, "g"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Petersilie", 0.5, "Bund"),
        ]
    },

    # === TOMATEN-GRUPPE ===
    {
        "name": "Chili con Carne",
        "description": "Würziges Chili mit Hackfleisch, Bohnen und Mais. Dazu Reis oder Brot.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 30,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 0,
        "cost_level": "guenstig",
        "tags": ["eintopf", "hackfleisch", "wuerschzig"],
        "ingredients": [
            ("Hackfleisch (gemischt)", 500, "g"),
            ("Zwiebeln", 1, "Stück"),
            ("Knoblauch", 2, "Zehe"),
            ("Paprika", 1, "Stück"),
            ("Passierte Tomaten", 400, "ml"),
            ("Kidneybohnen (Dose)", 1, "Dose"),
            ("Mais (Dose)", 1, "Dose"),
            ("Tomatenmark", 2, "EL"),
            ("Kreuzkümmel", 1, "TL"),
            ("Paprikapulver", 1, "TL"),
            ("Chiliflocken", 1, "Prise"),
            ("Reis", 300, "g"),
            ("Sonnenblumenöl", 1, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Schmand", 1, "Becher"),
        ]
    },
    {
        "name": "Shakshuka",
        "description": "Eier in würziger Tomatensauce – einfach, schnell und sättigend.",
        "base_servings": 4, "prep_time_minutes": 5, "cook_time_minutes": 20,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 0, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["pfanne", "eier", "vegetarisch"],
        "ingredients": [
            ("Eier", 6, "Stück"),
            ("Passierte Tomaten", 500, "ml"),
            ("Paprika", 1, "Stück"),
            ("Zwiebeln", 1, "Stück"),
            ("Knoblauch", 2, "Zehe"),
            ("Tomatenmark", 1, "EL"),
            ("Kreuzkümmel", 1, "TL"),
            ("Paprikapulver", 1, "TL"),
            ("Chiliflocken", 1, "Prise"),
            ("Olivenöl", 2, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Petersilie", 0.5, "Bund"),
            ("Feta", 80, "g"),
            ("Brot / Brötchen", 4, "Stück"),
        ]
    },
    {
        "name": "Pizza vom Blech",
        "description": "Schnelle Familienpizza mit Tomatensauce, Käse und Lieblingsbelag.",
        "base_servings": 4, "prep_time_minutes": 15, "cook_time_minutes": 20,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["ofen", "pizza", "klassiker"],
        "ingredients": [
            ("Pizzateig (fertig)", 1, "Stück"),
            ("Passierte Tomaten", 200, "ml"),
            ("Mozzarella", 2, "Stück"),
            ("Champignons", 100, "g"),
            ("Paprika", 1, "Stück"),
            ("Speck / Schinken", 100, "g"),
            ("Oregano (getr.)", 1, "TL"),
            ("Olivenöl", 1, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
        ]
    },

    # === ASIA-GRUPPE ===
    {
        "name": "Gebratener Reis mit Gemüse",
        "description": "Asiatischer gebratener Reis mit Ei, Gemüse und Sojasauce.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 15,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["reis", "asia", "vegetarisch"],
        "ingredients": [
            ("Reis", 300, "g"),
            ("Eier", 3, "Stück"),
            ("Karotten", 2, "Stück"),
            ("Tiefkühl-Erbsen", 150, "g"),
            ("Frühlingszwiebeln", 1, "Bund"),
            ("Sojasauce", 3, "EL"),
            ("Sonnenblumenöl", 2, "EL"),
            ("Knoblauch", 2, "Zehe"),
            ("Ingwer", 1, "Stück"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
        ]
    },
    {
        "name": "Rotes Thai-Curry",
        "description": "Cremiges Curry mit Hähnchen, Gemüse und Kokosmilch. Dazu Reis.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 20,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 0, "is_quick": 1,
        "cost_level": "mittel",
        "tags": ["reis", "asia", "curry", "haehnchen"],
        "ingredients": [
            ("Hähnchenbrust", 500, "g"),
            ("Reis", 300, "g"),
            ("Kokosmilch", 1, "Dose"),
            ("Paprika", 1, "Stück"),
            ("Zucchini", 1, "Stück"),
            ("Currypaste", 2, "EL"),
            ("Sojasauce", 1, "EL"),
            ("Zwiebeln", 1, "Stück"),
            ("Knoblauch", 2, "Zehe"),
            ("Ingwer", 1, "Stück"),
            ("Basilikum (frisch)", 0.5, "Bund"),
            ("Sonnenblumenöl", 1, "EL"),
            ("Salz", 1, "Prise"),
        ]
    },
    {
        "name": "Asia-Nudelpfanne",
        "description": "Schnelle Nudelpfanne mit knackigem Gemüse und Sojasauce.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 10,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["asia", "nudeln", "vegetarisch", "schnell"],
        "ingredients": [
            ("Asia-Nudeln", 400, "g"),
            ("Brokkoli", 1, "Stück"),
            ("Karotten", 2, "Stück"),
            ("Paprika", 1, "Stück"),
            ("Frühlingszwiebeln", 1, "Bund"),
            ("Sojasauce", 3, "EL"),
            ("Knoblauch", 2, "Zehe"),
            ("Ingwer", 1, "Stück"),
            ("Sonnenblumenöl", 2, "EL"),
            ("Salz", 1, "Prise"),
        ]
    },

    # === EINFACH & SCHNELL ===
    {
        "name": "Omelett mit Gemüse",
        "description": "Lockeres Omelett mit Paprika, Tomaten und Käse.",
        "base_servings": 2, "prep_time_minutes": 5, "cook_time_minutes": 10,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["eier", "schnell", "vegetarisch"],
        "ingredients": [
            ("Eier", 6, "Stück"),
            ("Paprika", 1, "Stück"),
            ("Tomaten", 2, "Stück"),
            ("Geriebener Käse", 60, "g"),
            ("Butter", 20, "g"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
        ]
    },
    {
        "name": "Couscous-Salat",
        "description": "Frischer Couscous-Salat mit Gurke, Tomaten, Feta und Zitrone.",
        "base_servings": 4, "prep_time_minutes": 15, "cook_time_minutes": 0,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 0, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["salat", "vegetarisch", "schnell"],
        "ingredients": [
            ("Couscous", 300, "g"),
            ("Tomaten", 3, "Stück"),
            ("Gurke", 1, "Stück"),
            ("Feta", 150, "g"),
            ("Zitrone", 1, "Stück"),
            ("Olivenöl", 3, "EL"),
            ("Petersilie", 0.5, "Bund"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
        ]
    },
    {
        "name": "Bratwurst mit Kartoffelpüree",
        "description": "Klassiker: Bratwurst mit cremigem Püree und Erbsen.",
        "base_servings": 4, "prep_time_minutes": 5, "cook_time_minutes": 20,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["deutsch", "klassiker", "schnell"],
        "ingredients": [
            ("Bratwurst", 4, "Stück"),
            ("Kartoffeln", 800, "g"),
            ("Milch", 100, "ml"),
            ("Butter", 30, "g"),
            ("Tiefkühl-Erbsen", 200, "g"),
            ("Muskatnuss", 1, "Prise"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Senf", 2, "EL"),
            ("Sonnenblumenöl", 1, "EL"),
        ]
    },

    # === WEITERE ALLTAGSGERICHTE ===
    {
        "name": "Gemüse-Curry mit Süßkartoffel",
        "description": "Veganes Curry mit Süßkartoffel und Kokosmilch. Wärmend und sättigend.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 25,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 0, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["curry", "vegetarisch", "vegan"],
        "ingredients": [
            ("Süßkartoffel", 2, "Stück"),
            ("Kokosmilch", 1, "Dose"),
            ("Spinat (frisch)", 200, "g"),
            ("Zwiebeln", 1, "Stück"),
            ("Knoblauch", 2, "Zehe"),
            ("Ingwer", 1, "Stück"),
            ("Currypaste", 2, "EL"),
            ("Reis", 300, "g"),
            ("Sonnenblumenöl", 1, "EL"),
            ("Salz", 1, "Prise"),
        ]
    },
    {
        "name": "Lachs mit Brokkoli und Reis",
        "description": "Gebratener Lachs mit gedämpftem Brokkoli und Reis.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 15,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "teuer",
        "tags": ["fisch", "reis", "gesund"],
        "ingredients": [
            ("Lachs-Filet", 600, "g"),
            ("Reis", 300, "g"),
            ("Brokkoli", 1, "Stück"),
            ("Zitrone", 1, "Stück"),
            ("Butter", 20, "g"),
            ("Olivenöl", 1, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
        ]
    },
    {
        "name": "Tomatensuppe mit Grilled Cheese",
        "description": "Cremige Tomatensuppe mit geröstetem Käse-Sandwich.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 20,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["suppe", "vegetarisch", "comfort"],
        "ingredients": [
            ("Passierte Tomaten", 800, "ml"),
            ("Zwiebeln", 1, "Stück"),
            ("Knoblauch", 2, "Zehe"),
            ("Sahne", 100, "ml"),
            ("Gemüsebrühe", 200, "ml"),
            ("Brot / Brötchen", 4, "Stück"),
            ("Geriebener Käse", 120, "g"),
            ("Butter", 30, "g"),
            ("Oregano (getr.)", 1, "TL"),
            ("Zucker", 1, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
        ]
    },
    {
        "name": "Zucchini-Frittata",
        "description": "Italienische Eierspeise mit Zucchini und Parmesan aus dem Ofen.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 20,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["eier", "ofen", "vegetarisch"],
        "ingredients": [
            ("Eier", 6, "Stück"),
            ("Zucchini", 2, "Stück"),
            ("Zwiebeln", 1, "Stück"),
            ("Parmesan", 40, "g"),
            ("Sahne", 50, "ml"),
            ("Olivenöl", 2, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Basilikum (frisch)", 0.5, "Bund"),
        ]
    },
    {
        "name": "Spinat-Nudeln mit Frischkäse",
        "description": "Schnelle cremige Pasta mit Spinat und Frischkäse-Sauce.",
        "base_servings": 4, "prep_time_minutes": 5, "cook_time_minutes": 15,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["pasta", "vegetarisch", "schnell"],
        "ingredients": [
            ("Penne", 500, "g"),
            ("Spinat (frisch)", 300, "g"),
            ("Frischkäse", 200, "g"),
            ("Knoblauch", 2, "Zehe"),
            ("Muskatnuss", 1, "Prise"),
            ("Olivenöl", 1, "EL"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
            ("Parmesan", 30, "g"),
        ]
    },
    {
        "name": "Flammkuchen",
        "description": "Dünner Teig mit Crème fraîche, Speck und Zwiebeln.",
        "base_servings": 4, "prep_time_minutes": 15, "cook_time_minutes": 15,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["ofen", "schnell", "deutsch"],
        "ingredients": [
            ("Pizzateig (fertig)", 1, "Stück"),
            ("Crème fraîche", 1, "Becher"),
            ("Speck / Schinken", 150, "g"),
            ("Zwiebeln", 2, "Stück"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
        ]
    },
    {
        "name": "Thunfisch-Wrap",
        "description": "Schnelle Wraps mit Thunfisch, Mais, Salat und Joghurt.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 0,
        "difficulty": "einfach", "is_vegetarian": 0, "is_kid_friendly": 1, "is_quick": 1,
        "cost_level": "guenstig",
        "tags": ["wraps", "fisch", "schnell"],
        "ingredients": [
            ("Thunfisch (Dose)", 2, "Dose"),
            ("Tortilla-Wraps", 4, "Stück"),
            ("Mais (Dose)", 1, "Dose"),
            ("Eisbergsalat", 0.5, "Stück"),
            ("Tomaten", 2, "Stück"),
            ("Joghurt (natur)", 1, "Becher"),
            ("Zitrone", 0.5, "Stück"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
        ]
    },
    {
        "name": "Gemüse-Kartoffel-Gratin",
        "description": "Überbackene Kartoffeln mit Gemüse und Käsekruste.",
        "base_servings": 4, "prep_time_minutes": 15, "cook_time_minutes": 35,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 1, "is_quick": 0,
        "cost_level": "guenstig",
        "tags": ["ofen", "kartoffel", "vegetarisch"],
        "ingredients": [
            ("Kartoffeln", 800, "g"),
            ("Zucchini", 1, "Stück"),
            ("Karotten", 2, "Stück"),
            ("Sahne", 200, "ml"),
            ("Geriebener Käse", 150, "g"),
            ("Knoblauch", 1, "Zehe"),
            ("Muskatnuss", 1, "Prise"),
            ("Butter", 10, "g"),
            ("Salz", 1, "Prise"),
            ("Pfeffer", 1, "Prise"),
        ]
    },
    {
        "name": "Tofu-Gemüsepfanne",
        "description": "Knuspriger Tofu mit buntem Gemüse und Sojasauce. Dazu Reis.",
        "base_servings": 4, "prep_time_minutes": 10, "cook_time_minutes": 15,
        "difficulty": "einfach", "is_vegetarian": 1, "is_kid_friendly": 0, "is_quick": 1,
        "cost_level": "mittel",
        "tags": ["asia", "tofu", "vegetarisch"],
        "ingredients": [
            ("Tofu", 400, "g"),
            ("Brokkoli", 1, "Stück"),
            ("Paprika", 1, "Stück"),
            ("Karotten", 2, "Stück"),
            ("Reis", 300, "g"),
            ("Sojasauce", 3, "EL"),
            ("Knoblauch", 2, "Zehe"),
            ("Ingwer", 1, "Stück"),
            ("Sonnenblumenöl", 2, "EL"),
            ("Frühlingszwiebeln", 1, "Bund"),
            ("Salz", 1, "Prise"),
        ]
    },
]


def seed_database(conn):
    """Populate database with ingredients and recipes."""
    # Check if already seeded
    count = conn.execute("SELECT COUNT(*) FROM ingredient").fetchone()[0]
    if count > 0:
        return

    # Insert ingredients
    ingredient_map = {}
    for ing in INGREDIENTS:
        cursor = conn.execute(
            "INSERT INTO ingredient (name, category, unit, cost_level, is_staple) VALUES (?, ?, ?, ?, ?)",
            (ing["name"], ing["category"], ing["unit"], ing["cost_level"], ing["is_staple"])
        )
        ingredient_map[ing["name"]] = cursor.lastrowid

    # Insert recipes and their ingredients
    for recipe in RECIPES:
        cursor = conn.execute(
            """INSERT INTO recipe (name, description, base_servings, prep_time_minutes,
               cook_time_minutes, difficulty, is_vegetarian, is_kid_friendly, is_quick,
               cost_level, tags) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (recipe["name"], recipe["description"], recipe["base_servings"],
             recipe["prep_time_minutes"], recipe["cook_time_minutes"], recipe["difficulty"],
             recipe["is_vegetarian"], recipe["is_kid_friendly"], recipe["is_quick"],
             recipe["cost_level"], str(recipe["tags"]))
        )
        recipe_id = cursor.lastrowid

        for ing_name, quantity, unit in recipe["ingredients"]:
            if ing_name not in ingredient_map:
                raise ValueError(f"Unknown ingredient: {ing_name}")
            conn.execute(
                "INSERT INTO recipe_ingredient (recipe_id, ingredient_id, quantity, unit) VALUES (?, ?, ?, ?)",
                (recipe_id, ingredient_map[ing_name], quantity, unit)
            )

    conn.commit()
