"""
Diet Plan Generator using Hugging Face LLMs
"""
import os
import sys
from typing import Dict, Any, Optional
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import requests
    import json
    from huggingface_hub import InferenceClient
except ImportError as e:
    print(f"Error importing required libraries: {e}")
    print("Please install required packages: pip install -r requirements.txt")
    sys.exit(1)

from config import MODEL_CONFIG, PROMPT_TEMPLATES
from user_profile import UserProfile


class DietPlanGenerator:
    """
    Main class for generating personalized diet plans using Hugging Face Inference API
    """
    
    def __init__(self, model_name: Optional[str] = None, api_token: Optional[str] = None):
        """
        Initialize the diet plan generator using Hugging Face Inference API
        
        Args:
            model_name (str, optional): Name of the Hugging Face model to use
            api_token (str, optional): Hugging Face API token (optional for public models)
        """
        self.model_name = model_name or MODEL_CONFIG["model_name"]
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN")
        self.client = None
        self.api_url = f"https://api-inference.huggingface.co/models/{self.model_name}"
        
        print(f"Initializing Diet Plan Generator with model: {self.model_name}")
        print(f"Using Hugging Face Inference API")
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Hugging Face Inference Client"""
        try:
            # Use direct API calls which are more reliable
            print("✓ Using direct API calls to Hugging Face Inference API")
            if self.api_token:
                print("✓ API token provided - ready for inference")
                # Test the connection
                self._test_api_connection()
            else:
                print("❌ API token is required for Hugging Face Inference API")
                print("💡 Get your free token at: https://huggingface.co/settings/tokens")
                print("💡 Set environment variable: HUGGINGFACE_API_TOKEN=your_token_here")
                print("💡 Or use --token your_token_here in command line")
            
            self.client = None  # Force direct API calls
            
        except Exception as e:
            print(f"Error during initialization: {e}")
            self.client = None
    
    def _test_api_connection(self):
        """Test the API connection with a simple request"""
        try:
            print("🔍 Testing API connection...")
            test_prompt = "Hello"
            
            # Using direct API call (more reliable)
            result = self._direct_api_call(test_prompt, max_new_tokens=5)
            if result and len(result.strip()) > 0:
                print("✅ API connection successful!")
            else:
                print("⚠️  API returned empty result, but connection works")
                
        except Exception as e:
            error_msg = str(e) if str(e) else "Unknown API error"
            print(f"⚠️  API test failed: {error_msg}")
            print("Will proceed anyway - API might be loading")
            
            # Additional debugging info
            if "503" in error_msg or "loading" in error_msg.lower():
                print("💡 Model is likely still loading on Hugging Face servers")
            elif "401" in error_msg or "unauthorized" in error_msg.lower():
                print("💡 Consider using an API token for better access")
            elif "429" in error_msg or "rate" in error_msg.lower():
                print("💡 Rate limited - try again in a few minutes or use API token")
            elif "connection" in error_msg.lower():
                print("💡 Check your internet connection")
    
    def _direct_api_call(self, prompt: str, max_new_tokens: int = None) -> str:
        """Make direct API call to Hugging Face Inference API with retry logic"""
        if not self.api_token:
            raise Exception("Hugging Face API token is required. Please set HUGGINGFACE_API_TOKEN environment variable or provide token in constructor.")
        
        headers = {"Authorization": f"Bearer {self.api_token}"}
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_new_tokens or MODEL_CONFIG["max_new_tokens"],
                "temperature": MODEL_CONFIG["temperature"],
                "top_p": MODEL_CONFIG["top_p"],
                "do_sample": MODEL_CONFIG["do_sample"],
                "return_full_text": False
            }
        }
        
        # Retry logic
        for attempt in range(MODEL_CONFIG.get("retry_attempts", 3)):
            try:
                response = requests.post(
                    self.api_url, 
                    headers=headers, 
                    json=payload,
                    timeout=MODEL_CONFIG.get("timeout_seconds", 30)
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get("generated_text", "")
                    else:
                        return str(result)
                        
                elif response.status_code == 503:
                    # Model is loading, wait and retry
                    print(f"⏳ Model is loading, retrying in {(attempt + 1) * 5} seconds...")
                    import time
                    time.sleep((attempt + 1) * 5)
                    continue
                    
                else:
                    error_msg = f"API call failed: {response.status_code} - {response.text}"
                    if attempt == MODEL_CONFIG.get("retry_attempts", 3) - 1:
                        raise Exception(error_msg)
                    else:
                        print(f"⚠️  Attempt {attempt + 1} failed: {error_msg}")
                        
            except requests.exceptions.Timeout:
                if attempt == MODEL_CONFIG.get("retry_attempts", 3) - 1:
                    raise Exception("API call timed out")
                else:
                    print(f"⚠️  Attempt {attempt + 1} timed out, retrying...")
                    
            except requests.exceptions.RequestException as e:
                if attempt == MODEL_CONFIG.get("retry_attempts", 3) - 1:
                    raise Exception(f"Network error: {e}")
                else:
                    print(f"⚠️  Network error on attempt {attempt + 1}: {e}")
        
        raise Exception("All retry attempts failed")
    
    def _create_diet_prompt(self, user_profile: UserProfile) -> str:
        """
        Create a detailed prompt for diet plan generation
        
        Args:
            user_profile (UserProfile): User's profile information
            
        Returns:
            str: Formatted prompt for the model
        """
        # Get dietary considerations
        considerations = user_profile.get_dietary_considerations()
        
        # Format diseases for better readability
        diseases_str = ", ".join(user_profile.diseases)
        if diseases_str == "none":
            diseases_str = "No specific health conditions"
        
        # Create dietary restrictions text based on food habit
        if user_profile.food_habit == "vegetarian":
            dietary_restrictions = """
            - NO meat, chicken, fish, seafood, beef, pork, lamb, turkey, duck, or ANY animal flesh
            - YES to: vegetables, fruits, grains, dairy, eggs, legumes, nuts, seeds, tofu, paneer
            - ONLY plant-based proteins: lentils, beans, chickpeas, tofu, paneer, nuts, eggs
            """
        elif user_profile.food_habit == "non-vegetarian":
            dietary_restrictions = "Include both plant-based and animal-based foods (meat, fish, poultry, etc.)"
        else:  # both
            dietary_restrictions = "Mix of vegetarian and non-vegetarian options"
        
        # Create detailed prompt
        prompt = PROMPT_TEMPLATES["diet_plan_prompt"].format(
            age=user_profile.age,
            weight=user_profile.weight,
            nationality=user_profile.nationality,
            food_habit=user_profile.food_habit.upper(),
            diseases=diseases_str,
            dietary_restrictions=dietary_restrictions
        )
        
        # Add additional context
        if considerations["special_needs"]:
            prompt += f"\nSpecial requirements: {', '.join(considerations['special_needs'])}"
        
        prompt += f"\nAge group: {considerations['age_group']}, BMI: {considerations['bmi']}"
        
        return prompt
    
    def _filter_non_vegetarian_content(self, diet_plan: str, food_habit: str) -> str:
        """
        Filter out non-vegetarian content if user selected vegetarian
        """
        if food_habit != "vegetarian":
            return diet_plan
        
        import re
        
        # Comprehensive list of non-vegetarian items to replace
        vegetarian_replacements = {
            # Poultry
            'chicken': 'paneer',
            'chicken breast': 'tofu steaks',
            'chicken curry': 'paneer curry',
            'chicken tikka': 'paneer tikka',
            'roasted chicken': 'roasted cauliflower',
            'grilled chicken': 'grilled paneer',
            'turkey': 'tempeh',
            'duck': 'mushrooms',
            
            # Red meat
            'beef': 'tofu',
            'beef curry': 'mushroom curry',
            'pork': 'jackfruit',
            'lamb': 'lentils',
            'mutton': 'chickpeas',
            'goat': 'black beans',
            'steak': 'grilled portobello',
            'bacon': 'coconut bacon',
            'ham': 'seitan',
            'sausage': 'vegetarian sausage',
            'pepperoni': 'spiced tempeh',
            
            # Seafood
            'fish': 'tofu',
            'fish curry': 'vegetable curry',
            'salmon': 'marinated tofu',
            'tuna': 'chickpea salad',
            'cod': 'cauliflower',
            'shrimp': 'mushrooms',
            'prawns': 'bell peppers',
            'crab': 'jackfruit',
            'lobster': 'king oyster mushrooms',
            'seafood': 'mixed vegetables',
            
            # Generic terms
            'meat': 'plant protein',
            'non-veg': 'vegetarian',
            'animal protein': 'plant protein'
        }
        
        filtered_plan = diet_plan
        
        # Apply replacements with word boundaries to avoid partial matches
        for non_veg_item, veg_replacement in vegetarian_replacements.items():
            # Use word boundaries for better matching
            pattern = re.compile(r'\b' + re.escape(non_veg_item) + r'\b', re.IGNORECASE)
            filtered_plan = pattern.sub(veg_replacement, filtered_plan)
        
        # Add a note if any replacements were made
        if filtered_plan != diet_plan:
            filtered_plan += "\n\nNote: This diet plan has been customized for vegetarian preferences."
        
        return filtered_plan
    
    def generate_diet_plan(self, user_profile: UserProfile) -> str:
        """
        Generate a personalized diet plan for the user using Hugging Face Inference API
        
        Args:
            user_profile (UserProfile): User's profile information
            
        Returns:
            str: Generated diet plan
        """
        print("Generating personalized diet plan using Hugging Face API...")
        
        # Create the prompt
        prompt = self._create_diet_prompt(user_profile)
        
        try:
            # Use direct API call (more reliable than InferenceClient)
            print("🔄 Using Hugging Face API...")
            generated_text = self._direct_api_call(prompt)
            
            # Clean up the output
            diet_plan = self._clean_generated_text(generated_text, prompt)
            
            # Filter non-vegetarian content if user is vegetarian
            diet_plan = self._filter_non_vegetarian_content(diet_plan, user_profile.food_habit)
            
            return diet_plan
            
        except Exception as e:
            error_msg = str(e) if str(e) else "Unknown API error"
            print(f"Error generating diet plan via API: {error_msg}")
            
            # Provide helpful error context
            if "503" in error_msg:
                print("💡 The model is loading on Hugging Face servers. This is normal for the first request.")
            elif "401" in error_msg:
                print("💡 Authentication error. Consider using an API token.")
            elif "429" in error_msg:
                print("💡 Rate limited. Try again in a few minutes or use an API token.")
            elif "connection" in error_msg.lower():
                print("💡 Check your internet connection.")
            
            print("Using local fallback plan...")
            return self._generate_fallback_diet_plan(user_profile)
    
    def _clean_generated_text(self, generated_text: str, original_prompt: str) -> str:
        """
        Clean and format the generated text
        
        Args:
            generated_text (str): Raw generated text from model
            original_prompt (str): Original prompt used
            
        Returns:
            str: Cleaned and formatted text
        """
        # Remove the original prompt if it appears in the output
        if original_prompt in generated_text:
            generated_text = generated_text.replace(original_prompt, "").strip()
        
        # Remove any incomplete sentences at the end
        sentences = generated_text.split('.')
        if len(sentences) > 1 and len(sentences[-1].strip()) < 20:
            generated_text = '.'.join(sentences[:-1]) + '.'
        
        # Basic formatting
        generated_text = generated_text.strip()
        
        return generated_text
    
    def _generate_fallback_diet_plan(self, user_profile: UserProfile) -> str:
        """
        Generate a basic diet plan if the model fails
        
        Args:
            user_profile (UserProfile): User's profile information
            
        Returns:
            str: Basic diet plan template
        """
        considerations = user_profile.get_dietary_considerations()
        
        fallback_plan = f"""
PERSONALIZED DIET PLAN

Profile Summary:
- Age: {user_profile.age} years ({considerations['age_group']})
- Weight: {user_profile.weight} kg (BMI: {considerations['bmi']})
- Cuisine Preference: {user_profile.nationality}
- Health Conditions: {', '.join(user_profile.diseases)}

DAILY MEAL PLAN:

BREAKFAST:
- Whole grain cereal with low-fat milk or plant-based alternative
- Fresh fruit (banana, berries, or seasonal fruit)
- Green tea or herbal tea

LUNCH:
- Lean protein (chicken, fish, tofu, or legumes)
- Complex carbohydrates (brown rice, quinoa, or whole wheat bread)
- Mixed vegetables (steamed or lightly sautéed)
- Small portion of healthy fats (nuts, avocado, or olive oil)

DINNER:
- Light protein source
- Large portion of vegetables
- Small portion of complex carbs
- Herbal tea

SNACKS:
- Fresh fruits
- Nuts (small portion)
- Yogurt or plant-based alternative

SPECIAL CONSIDERATIONS:
"""
        
        # Add specific recommendations based on health conditions
        for disease in user_profile.diseases:
            if "diabetes" in disease.lower():
                fallback_plan += "- Monitor carbohydrate intake and choose low glycemic index foods\n"
            elif "hypertension" in disease.lower():
                fallback_plan += "- Limit sodium intake and include potassium-rich foods\n"
            elif "cholesterol" in disease.lower():
                fallback_plan += "- Limit saturated fats and choose lean proteins\n"
                fallback_plan += "- Include high-fiber foods like oats, beans, and vegetables\n"
                fallback_plan += "- Add omega-3 rich foods like fish, walnuts, and flaxseeds\n"
            elif "heart" in disease.lower():
                fallback_plan += "- Include omega-3 rich foods and limit saturated fats\n"
        
        fallback_plan += "\nHYDRATION:\n- Drink 8-10 glasses of water daily\n- Limit sugary drinks and alcohol"
        fallback_plan += "\n\nNote: This is a general plan. Please consult with a healthcare provider for personalized medical advice."
        
        return fallback_plan
    
    def save_diet_plan(self, diet_plan: str, user_profile: UserProfile, filename: Optional[str] = None):
        """
        Save the generated diet plan to a file
        
        Args:
            diet_plan (str): Generated diet plan
            user_profile (UserProfile): User's profile
            filename (str, optional): Custom filename
        """
        if filename is None:
            filename = f"diet_plan_{user_profile.age}y_{user_profile.weight}kg.txt"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"=== PERSONALIZED DIET PLAN ===\n\n")
                f.write(f"Generated for: {user_profile}\n")
                f.write(f"Generated on: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Model used: {self.model_name}\n\n")
                f.write("=" * 50 + "\n\n")
                f.write(diet_plan)
                f.write("\n\n" + "=" * 50)
                f.write("\nDisclaimer: This diet plan is generated by AI and should not replace professional medical advice.")
            
            print(f"✓ Diet plan saved to: {filename}")
            
        except Exception as e:
            print(f"Error saving diet plan: {e}")


if __name__ == "__main__":
    # Test the DietPlanGenerator
    print("Testing Diet Plan Generator...")
    
    try:
        # Create a test user profile
        test_profile = UserProfile(
            age=30,
            weight=75.0,
            nationality="Indian",
            diseases=["diabetes", "hypertension"]
        )
        
        # Initialize generator
        generator = DietPlanGenerator()
        
        # Generate diet plan
        diet_plan = generator.generate_diet_plan(test_profile)
        
        print("\n" + "="*60)
        print("GENERATED DIET PLAN:")
        print("="*60)
        print(diet_plan)
        
        # Save the plan
        generator.save_diet_plan(diet_plan, test_profile)
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()