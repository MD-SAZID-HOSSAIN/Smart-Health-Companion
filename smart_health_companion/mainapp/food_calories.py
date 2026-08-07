# Calorie lookup table for the 16 dish classes recognised by the food model.
# Values are kilocalories per 100 grams.
# Keys MUST match the class_names list stored in the model checkpoint.

FOOD_CALORIES = {
    "khichuri": 130,
    "chickpeas": 140,
    "biryani": 150,
    "eggomlete": 150,
    "roshgolla": 150,
    "morogpolao": 160,
    "haleem": 160,
    "roshmalai": 190,
    "hilshfish": 220,
    "kabab": 220,
    "nehari": 220,
    "yogurt": 170,
    "beguni": 250,
    "kalabhuna": 320,
    "porota": 300,
    "bakorkhani": 430,
}

# Separate mapping just for pretty display text in the UI - keeps the
# lookup table matching the model exactly while still showing nice names
DISPLAY_NAMES = {
    "khichuri": "Khichuri",
    "chickpeas": "Chickpeas (cholar dal)",
    "biryani": "Biryani",
    "eggomlete": "Egg Omelette",
    "roshgolla": "Roshgolla",
    "morogpolao": "Morog Polao",
    "haleem": "Haleem",
    "roshmalai": "Roshmalai",
    "hilshfish": "Hilsha Fish (Curry)",
    "kabab": "Kabab",
    "nehari": "Nehari",
    "yogurt": "Yogurt (Doi)",
    "beguni": "Beguni",
    "kalabhuna": "Kala Bhuna",
    "porota": "Porota",
    "bakorkhani": "Bakorkhani",
}
