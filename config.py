"""
Configuration settings for the Diet Plan Generator
"""

# Hugging Face Model Configuration for Local Inference
MODEL_CONFIG = {
    # Using Meta Llama 3.2 via Hugging Face Inference API
    "model_name": "meta-llama/Llama-3.2-3B-Instruct",  # 3B params, instruction-tuned
    
    # Alternative models if Llama doesn't work:
    # "model_name": "meta-llama/Llama-3.2-1B-Instruct",  # Smaller Llama (1B)
    # "model_name": "google/flan-t5-large",  # Reliable fallback (780M params)
    # "model_name": "google/flan-t5-base",  # Smaller, faster (250M params)
    
    # Note: Meta Llama models require license acceptance at huggingface.co
    # and may need special Inference API access
    
    # GPT-style models (less suitable for this task):
    # "model_name": "distilgpt2",  # Small and fast (80MB), but not instruction-tuned
    # "model_name": "openai-community/gpt2",  # Standard GPT-2 (500MB)
    
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