"""
Diet Plan Generator using Hugging Face Inference API
Clean API-only implementation with Meta Llama models
"""
import os
import re
from typing import Dict, Any, Optional
import requests
import json
from huggingface_hub import InferenceClient

from config import MODEL_CONFIG, PROMPT_TEMPLATES
from user_profile import UserProfile


class DietPlanGenerator:
    """Main class for generating personalized diet plans using Hugging Face Inference API only"""
    
    def __init__(self, model_name: Optional[str] = None, api_token: Optional[str] = None):
        """Initialize the diet plan generator"""
        self.model_name = model_name or MODEL_CONFIG["model_name"]
        self.api_token = api_token or os.getenv("HUGGINGFACE_API_TOKEN")
        
        if not self.api_token:
            raise Exception("Hugging Face API token is required.")
        
        print(f"Initializing Diet Plan Generator with model: {self.model_name}")
        print("Using Hugging Face Inference API with InferenceClient...")
        
        # Initialize InferenceClient for better Llama support
        self.client = InferenceClient(token=self.api_token)
        
        # Test API but don't fail initialization - we'll check on actual generation
        test_result = self._test_api_connection()
        if test_result:
            print("✅ API connection test successful!")
        else:
            print("⚠️  API test inconclusive, will proceed with generation...")
    
    def _test_api_connection(self) -> bool:
        """Test if the Hugging Face Inference API is accessible"""
        if not self.api_token:
            return False
        
        try:
            api_url = f"https://huggingface.co/api/inference/models/{self.model_name}"
            headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}
            payload = {"inputs": "Hello", "options": {"wait_for_model": True}}
            
            print(f"🔍 Testing API: {api_url}")
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            
            if response.status_code == 404:
                # 404 is expected for Llama models with simple test queries
                # They only respond to chat_completion, not text-generation endpoints
                print(f"   ℹ️  Model uses chat_completion interface (expected for Llama models)")
                return True  # This is actually fine for Llama models
            elif response.status_code in [200, 400, 503]:
                return True
            elif response.status_code == 403:
                print(f"   ⚠️  Access denied - Accept license at: https://huggingface.co/{self.model_name}")
                return False
            else:
                print(f"   Response: {response.text[:200]}")
                return False
        except Exception as e:
            print(f"   API test error: {e}")
            return False
    
    def _call_api(self, prompt: str, max_new_tokens: int = None) -> str:
        """Make API call to Hugging Face with retry logic"""
        if not self.api_token:
            raise Exception("API token required.")
        
        # Try using InferenceClient first (better for Llama models)
        if "llama" in self.model_name.lower():
            return self._call_api_with_client(prompt, max_new_tokens)
        
        # Fallback to direct REST API for other models
        api_url = f"https://huggingface.co/api/inference/models/{self.model_name}"
        headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": max_new_tokens or 600, "temperature": 0.7, "top_p": 0.9, "return_full_text": False},
            "options": {"wait_for_model": True, "use_cache": False}
        }
        
        for attempt in range(MODEL_CONFIG.get("retry_attempts", 3)):
            try:
                response = requests.post(api_url, headers=headers, json=payload, timeout=60)
                
                print(f"📡 API Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        return result[0].get("generated_text", "")
                    return str(result)
                elif response.status_code == 503:
                    print(f"⏳ Model loading, retrying in {(attempt + 1) * 5}s...")
                    import time
                    time.sleep((attempt + 1) * 5)
                    continue
                elif response.status_code == 404:
                    error_msg = f"❌ Model '{self.model_name}' not found or not available via Inference API.\n"
                    error_msg += f"Response: {response.text[:300]}\n"
                    error_msg += f"Please check:\n"
                    error_msg += f"1. Model exists at https://huggingface.co/{self.model_name}\n"
                    error_msg += f"2. You have accepted the model's license\n"
                    error_msg += "3. The model supports Inference API (some models don't)"
                    raise Exception(error_msg)
                else:
                    error_msg = f"API call failed: {response.status_code}\nResponse: {response.text[:300]}"
                    if attempt == 2:
                        raise Exception(error_msg)
                    print(f"⚠️  Attempt {attempt + 1} failed, retrying...")
            except requests.exceptions.Timeout:
                if attempt == 2:
                    raise Exception("API call timed out")
                print(f"⏱️  Timeout on attempt {attempt + 1}, retrying...")
            except Exception as e:
                if attempt == 2:
                    raise
                print(f"❌ Error on attempt {attempt + 1}: {e}")
                import time
                time.sleep(2)
        
        raise Exception("Failed after all retry attempts")
    
    def _call_api_with_client(self, prompt: str, max_new_tokens: int = None) -> str:
        """Use InferenceClient for Llama models (better support)"""
        print(f"🦙 Using InferenceClient for Llama model with chat_completion...")
        
        try:
            # Llama models support 'conversational' task, so use chat_completion
            # Parse the Llama-formatted prompt to extract system and user messages
            messages = []
            
            # Check if prompt has Llama special tokens
            if "<|start_header_id|>system<|end_header_id|>" in prompt:
                # Extract system message
                system_start = prompt.find("<|start_header_id|>system<|end_header_id|>")
                system_end = prompt.find("<|eot_id|>", system_start)
                if system_start != -1 and system_end != -1:
                    system_content = prompt[system_start:system_end]
                    system_content = system_content.replace("<|start_header_id|>system<|end_header_id|>", "").strip()
                    messages.append({"role": "system", "content": system_content})
                
                # Extract user message
                user_start = prompt.find("<|start_header_id|>user<|end_header_id|>")
                user_end = prompt.find("<|eot_id|>", user_start)
                if user_start != -1 and user_end != -1:
                    user_content = prompt[user_start:user_end]
                    user_content = user_content.replace("<|start_header_id|>user<|end_header_id|>", "").strip()
                    messages.append({"role": "user", "content": user_content})
            else:
                # If no special tokens, treat entire prompt as user message
                messages.append({"role": "user", "content": prompt})
            
            # Use chat_completion for conversational models
            response = self.client.chat_completion(
                messages=messages,
                model=self.model_name,
                max_tokens=max_new_tokens or 600,
                temperature=0.7,
                top_p=0.9,
            )
            
            print(f"✅ InferenceClient chat_completion successful!")
            
            # Extract the generated text from the response
            if hasattr(response, 'choices') and len(response.choices) > 0:
                return response.choices[0].message.content
            else:
                return str(response)
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ InferenceClient error: {error_msg}")
            
            # Provide helpful error messages
            if "404" in error_msg or "not found" in error_msg.lower():
                raise Exception(
                    f"Model '{self.model_name}' not accessible.\n"
                    f"Please ensure:\n"
                    f"1. You've accepted the license at https://huggingface.co/{self.model_name}\n"
                    f"2. Your token has access to gated models\n"
                    f"3. The model supports serverless inference\n"
                    f"Original error: {error_msg}"
                )
            elif "403" in error_msg or "unauthorized" in error_msg.lower():
                raise Exception(
                    f"Access denied to '{self.model_name}'.\n"
                    f"Please accept the model license at: https://huggingface.co/{self.model_name}\n"
                    f"Original error: {error_msg}"
                )
            else:
                raise
    
    def _create_diet_prompt(self, user_profile: UserProfile) -> str:
        """Create prompt for diet plan generation"""
        # Make nationality/cuisine preference more prominent in system prompt
        cuisine_type = user_profile.nationality if user_profile.nationality else "Indian"
        
        # Calculate BMI for better personalization
        height_in_meters = (user_profile.height * 0.0254)  # Convert inches to meters
        bmi = user_profile.weight / (height_in_meters ** 2)
        bmi_category = "Normal"
        if bmi < 18.5:
            bmi_category = "Underweight"
        elif 18.5 <= bmi < 25:
            bmi_category = "Normal"
        elif 25 <= bmi < 30:
            bmi_category = "Overweight"
        else:
            bmi_category = "Obese"
        
        system_prompt = f"You are an expert nutritionist specializing in {cuisine_type} cuisine. Create personalized balanced diet plans with specific {cuisine_type} dish names and appropriate portions."
        
        user_prompt = f"""Create a daily {cuisine_type} diet plan for a person with these details:
- Age: {user_profile.age} years
- Weight: {user_profile.weight} kg
- Height: {user_profile.height} inches ({height_in_meters:.2f} meters)
- BMI: {bmi:.1f} ({bmi_category})
- Nationality/Cuisine: {cuisine_type}
- Food Preference: {user_profile.food_habit}
- Health Conditions: {user_profile.diseases}

IMPORTANT: Use ONLY traditional {cuisine_type} dishes. Do not mix cuisines.

Provide a structured meal plan with:

BREAKFAST: 2-3 {cuisine_type} dishes with portion sizes
LUNCH: 3-4 {cuisine_type} dishes with portion sizes  
DINNER: 2-3 {cuisine_type} dishes with portion sizes
SNACKS: Mid-morning and evening {cuisine_type} snacks

Example {cuisine_type} dishes you could include:
- For Indian: Masala Dosa, Paneer Tikka, Dal Tadka, Roti, Idli, Sambar, etc.
- Use authentic {cuisine_type} food items only."""
        
        if "llama" in self.model_name.lower():
            prompt = f"<|begin_of_text|><|start_header_id|>system<|end_header_id|>\n\n{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>\n\n{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>\n\n"
        else:
            prompt = f"{system_prompt}\n\n{user_prompt}\n\nDiet Plan:\n"
        return prompt
    
    def _filter_non_vegetarian_content(self, diet_plan: str, food_habit: str) -> str:
        """Filter non-veg content for vegetarians"""
        if food_habit.lower() != "vegetarian":
            return diet_plan
        
        non_veg_items = {'chicken', 'fish', 'meat', 'egg', 'mutton', 'lamb', 'beef', 'pork', 'prawn', 'shrimp', 'crab', 'turkey', 'duck', 'salmon', 'tuna'}
        lines = diet_plan.split('\n')
        filtered_lines = [line for line in lines if not any(item in line.lower() for item in non_veg_items)]
        return '\n'.join(filtered_lines)
    
    def _format_output_as_table(self, generated_text: str, user_profile: UserProfile) -> str:
        """Format LLM output into bulleted sections"""
        lines = generated_text.split('\n')
        meals = {'breakfast': [], 'lunch': [], 'dinner': [], 'snacks': []}
        current_meal = None
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 2:
                continue
            line_lower = line.lower()
            
            if 'breakfast' in line_lower:
                current_meal = 'breakfast'
                continue
            elif 'lunch' in line_lower:
                current_meal = 'lunch'
                continue
            elif 'dinner' in line_lower:
                current_meal = 'dinner'
                continue
            elif 'snack' in line_lower:
                current_meal = 'snacks'
                continue
            
            if current_meal:
                clean_line = re.sub(r'^\d+[\.)]\s*', '', line).lstrip('-*• ').strip()
                if clean_line and len(clean_line) > 3:
                    meals[current_meal].append(clean_line)
        
        # FALLBACK: If parsing failed to extract meals, use raw text and distribute items
        if not any(meals.values()):
            all_lines = [l.strip() for l in generated_text.split('\n') if l.strip()]
            for i, line in enumerate(all_lines[:12]):
                clean = re.sub(r'^\d+[\.)]\s*', '', line).lstrip('-*• ').strip()
                if clean and len(clean) > 3:
                    if i < 3:
                        meals['breakfast'].append(clean)
                    elif i < 6:
                        meals['lunch'].append(clean)
                    elif i < 9:
                        meals['dinner'].append(clean)
                    else:
                        meals['snacks'].append(clean)
        
        # Format as bulleted sections
        # FALLBACK: Show default message if no items parsed
        breakfast_list = '\n'.join([f"   • {item}" for item in meals['breakfast']]) if meals['breakfast'] else '   • [No specific items - please try again]'
        lunch_list = '\n'.join([f"   • {item}" for item in meals['lunch']]) if meals['lunch'] else '   • [No specific items - please try again]'
        dinner_list = '\n'.join([f"   • {item}" for item in meals['dinner']]) if meals['dinner'] else '   • [No specific items - please try again]'
        snacks_list = '\n'.join([f"   • {item}" for item in meals['snacks']]) if meals['snacks'] else '   • Fresh fruits, nuts, or healthy snacks (fallback)'
        
        # Calculate BMI for display
        height_in_meters = user_profile.height * 0.0254
        bmi = user_profile.weight / (height_in_meters ** 2)
        
        # Determine BMI category
        if bmi < 18.5:
            bmi_status = "Underweight ⚠️"
        elif 18.5 <= bmi < 25:
            bmi_status = "Normal ✅"
        elif 25 <= bmi < 30:
            bmi_status = "Overweight ⚠️"
        else:
            bmi_status = "Obese ⚠️"
        
        output = f"""

🍽️  PERSONALIZED DIET PLAN (AI Generated)


👤 PROFILE SUMMARY

   📊 Physical Stats:
      • Age: {user_profile.age} years
      • Weight: {user_profile.weight} kg
      • Height: {user_profile.height} inches ({height_in_meters:.2f} m)
      • BMI: {bmi:.1f} ({bmi_status})
   
   🌍 Dietary Preferences:
      • Cuisine Type: {user_profile.nationality}
      • Food Habit: {user_profile.food_habit.title()}
   
   🏥 Health Information:
      • Health Conditions: {', '.join(user_profile.diseases) if user_profile.diseases else 'None'}


🎯 ADDITIONAL TIPS FOR SUCCESS

   • Meal Prep: Prepare meals in advance to stay consistent
   • Read Labels: Check nutrition facts and ingredient lists
   • Mindful Eating: Eat slowly and listen to your body's hunger cues
   • Track Progress: Keep a food diary or use a nutrition app
   • Stay Consistent: Small daily changes lead to big results
   • Avoid Skipping Meals: Regular eating prevents overeating later
   • Include Variety: Rotate different foods to get diverse nutrients
   • Plan Ahead: Have healthy snacks ready to avoid unhealthy choices


📋 DAILY MEAL PLAN

🌅 BREAKFAST (Morning Meal)
{breakfast_list}

🌞 LUNCH (Afternoon Meal)
{lunch_list}

🌙 DINNER (Evening Meal)
{dinner_list}

🍎 SNACKS (Between Meals)
{snacks_list}


💧 HYDRATION & WELLNESS TIPS

💧 Hydration Guidelines:
   • Drink 8-10 glasses (2-3 liters) of water throughout the day
   • Start your morning with warm water and lemon
   • Carry a water bottle to track your intake

💡 General Wellness Tips:
   • Eat at regular intervals (every 3-4 hours)
   • Practice portion control - use smaller plates
   • Engage in at least 30 minutes of physical activity daily
   • Get 7-8 hours of quality sleep
   • Manage stress through meditation or yoga


⚠️  DISCLAIMER

   This is an AI-generated dietary guide based on the information provided.
   For specific medical conditions or personalized nutrition advice, please
   consult a registered dietitian or healthcare provider.

"""
        return output
    
    def generate_diet_plan(self, user_profile: UserProfile) -> str:
        """Generate personalized diet plan using API"""
        prompt = self._create_diet_prompt(user_profile)
        
        try:
            print("Generating diet plan with Hugging Face API...")
            generated_text = self._call_api(prompt, max_new_tokens=600)
            
            if generated_text and len(generated_text.strip()) > 50:
                filtered_text = self._filter_non_vegetarian_content(generated_text, user_profile.food_habit)
                diet_plan = self._format_output_as_table(filtered_text, user_profile)
                print("Diet plan generated successfully!")
                return diet_plan
            else:
                raise Exception("API generated insufficient content. Please try again.")
        except Exception as e:
            print(f"API generation failed: {e}")
            raise Exception(f"Failed to generate diet plan: {e}")
    
    def save_diet_plan(self, diet_plan: str, user_profile: UserProfile, filename: Optional[str] = None):
        """Save diet plan to file"""
        if filename is None:
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"diet_plan_{user_profile.name}_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(diet_plan)
        
        print(f"Diet plan saved to: {filename}")
        return filename
