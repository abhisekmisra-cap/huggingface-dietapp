"""
Configuration settings for the Diet Plan Generator
"""

# Hugging Face API Configuration
MODEL_CONFIG = {
    # Using models available via Hugging Face Inference API
    "model_name": "gpt2",  # Reliable model that works well with Inference API
    
    # Other good API models you can try:
    # "model_name": "microsoft/DialoGPT-medium",  # May have compatibility issues
    # "model_name": "microsoft/DialoGPT-small",
    # "model_name": "distilgpt2",  # Faster alternative
    # "model_name": "EleutherAI/gpt-neo-1.3B",  # Larger model, requires token
    # "model_name": "mistralai/Mistral-7B-Instruct-v0.1",  # Requires API token
    
    "max_new_tokens": 300,
    "temperature": 0.7,
    "top_p": 0.9,
    "do_sample": True,
    
    # API specific settings
    "retry_attempts": 3,
    "timeout_seconds": 30,
}

# Diet Plan Generation Settings
DIET_CONFIG = {
    "default_meals_per_day": 3,
    "include_snacks": True,
    "food_habits": [
        "vegetarian", "non-vegetarian", "both"
    ],
    "vegetarian_proteins": [
        "lentils", "chickpeas", "black beans", "kidney beans", "tofu", "tempeh", 
        "paneer", "cottage cheese", "quinoa", "nuts", "seeds", "yogurt"
    ],
    "dietary_restrictions": [
        "vegan", "gluten-free", "dairy-free", 
        "keto", "low-carb", "low-fat", "diabetic", "heart-healthy"
    ],
    "common_diseases": [
        "diabetes", "hypertension", "heart disease", "obesity", 
        "high cholesterol", "kidney disease", "celiac disease", 
        "food allergies", "none"
    ]
}

# User Input Validation
VALIDATION_CONFIG = {
    "age_range": (1, 120),
    "weight_range": (10, 500),  # in kg
    "supported_nationalities": [
        "American", "Indian", "Chinese", "Japanese", "Italian", 
        "Mexican", "French", "German", "British", "Mediterranean",
        "Middle Eastern", "African", "Other"
    ]
}

# Prompt Templates
PROMPT_TEMPLATES = {
    "diet_plan_prompt": """
    Generate a {food_habit} diet plan for:
    - Age: {age} years, Weight: {weight} kg
    - Cuisine: {nationality}
    - Health: {diseases}
    
    STRICT {food_habit} REQUIREMENTS:
    {dietary_restrictions}
    
    Create ONLY {food_habit} meals:
    Note: For vegetarian diets, NO EGGS allowed. For non-vegetarian diets, eggs are allowed.
    
    BREAKFAST ({food_habit} only):
    
    LUNCH ({food_habit} only):
    
    DINNER ({food_habit} only):
    
    SNACKS ({food_habit} only):
    
    Include portions and nutritional benefits for each meal.
    """,
    
    "system_prompt": """
    You are a professional nutritionist and dietitian with expertise in creating personalized diet plans. 
    Consider the person's age, weight, cultural background, and any health conditions when creating meal recommendations.
    Focus on balanced nutrition, proper portion sizes, and foods that are culturally appropriate and enjoyable.
    """
}