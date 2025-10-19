"""
User Profile class for handling and validating user inputs
"""
from typing import List, Optional, Dict, Any
from config import VALIDATION_CONFIG, DIET_CONFIG


class UserProfile:
    """
    Handles user profile information including validation and formatting
    """
    
    def __init__(self, age: int, weight: float, nationality: str, diseases: List[str], food_habit: str = "both"):
        """
        Initialize user profile with validation
        
        Args:
            age (int): User's age in years
            weight (float): User's weight in kg
            nationality (str): User's nationality or cuisine preference
            diseases (List[str]): List of health conditions/diseases
            food_habit (str): Food habit preference (vegetarian, non-vegetarian, or both)
        """
        self.age = self._validate_age(age)
        self.weight = self._validate_weight(weight)
        self.nationality = self._validate_nationality(nationality)
        self.diseases = self._validate_diseases(diseases)
        self.food_habit = self._validate_food_habit(food_habit)
    
    def _validate_age(self, age: int) -> int:
        """Validate age input"""
        if not isinstance(age, int):
            raise ValueError("Age must be an integer")
        
        min_age, max_age = VALIDATION_CONFIG["age_range"]
        if not (min_age <= age <= max_age):
            raise ValueError(f"Age must be between {min_age} and {max_age} years")
        
        return age
    
    def _validate_weight(self, weight: float) -> float:
        """Validate weight input"""
        if not isinstance(weight, (int, float)):
            raise ValueError("Weight must be a number")
        
        weight = float(weight)
        min_weight, max_weight = VALIDATION_CONFIG["weight_range"]
        if not (min_weight <= weight <= max_weight):
            raise ValueError(f"Weight must be between {min_weight} and {max_weight} kg")
        
        return weight
    
    def _validate_nationality(self, nationality: str) -> str:
        """Validate nationality input"""
        if not isinstance(nationality, str):
            raise ValueError("Nationality must be a string")
        
        nationality = nationality.strip().title()
        supported = VALIDATION_CONFIG["supported_nationalities"]
        
        if nationality not in supported:
            print(f"Warning: '{nationality}' not in supported nationalities. Using 'Other'")
            nationality = "Other"
        
        return nationality
    
    def _validate_diseases(self, diseases: List[str]) -> List[str]:
        """Validate and clean disease list"""
        if not isinstance(diseases, list):
            raise ValueError("Diseases must be provided as a list")
        
        # Clean and validate each disease
        validated_diseases = []
        common_diseases = DIET_CONFIG["common_diseases"]
        
        for disease in diseases:
            if not isinstance(disease, str):
                continue
            
            disease = disease.strip().lower()
            if disease == "":
                continue
            
            # Check if it's a common disease
            if disease in [d.lower() for d in common_diseases]:
                validated_diseases.append(disease)
            else:
                # Add custom diseases but warn user
                print(f"Warning: '{disease}' is not a common condition. Including anyway.")
                validated_diseases.append(disease)
        
        # If no diseases provided, set to "none"
        if not validated_diseases:
            validated_diseases = ["none"]
        
        return validated_diseases
    
    def _validate_food_habit(self, food_habit: str) -> str:
        """Validate food habit input"""
        if not isinstance(food_habit, str):
            raise ValueError("Food habit must be a string")
        
        food_habit = food_habit.strip().lower()
        supported_habits = [habit.lower() for habit in DIET_CONFIG["food_habits"]]
        
        if food_habit not in supported_habits:
            print(f"Warning: '{food_habit}' not in supported food habits. Using 'both'")
            food_habit = "both"
        
        return food_habit
    
    def get_bmi(self) -> float:
        """Calculate BMI (requires height, but we'll estimate based on age for now)"""
        # This is a simplified BMI calculation
        # In a real application, you'd want to collect height separately
        estimated_height = 1.7  # Average height in meters
        bmi = self.weight / (estimated_height ** 2)
        return round(bmi, 1)
    
    def get_age_category(self) -> str:
        """Categorize user by age group"""
        if self.age < 13:
            return "child"
        elif self.age < 20:
            return "teenager"
        elif self.age < 30:
            return "young_adult"
        elif self.age < 50:
            return "adult"
        elif self.age < 65:
            return "middle_aged"
        else:
            return "senior"
    
    def get_dietary_considerations(self) -> Dict[str, Any]:
        """Get dietary considerations based on profile"""
        considerations = {
            "age_group": self.get_age_category(),
            "bmi": self.get_bmi(),
            "health_conditions": self.diseases,
            "cuisine_preference": self.nationality,
            "food_habit": self.food_habit,
            "special_needs": []
        }
        
        # Add special dietary considerations based on conditions
        for disease in self.diseases:
            if "diabetes" in disease.lower():
                considerations["special_needs"].extend(["low-sugar", "complex-carbs", "fiber-rich"])
            elif "hypertension" in disease.lower() or "heart" in disease.lower():
                considerations["special_needs"].extend(["low-sodium", "heart-healthy", "omega-3"])
            elif "cholesterol" in disease.lower():
                considerations["special_needs"].extend(["low-saturated-fat", "high-fiber", "omega-3", "plant-sterols", "lean-protein"])
            elif "kidney" in disease.lower():
                considerations["special_needs"].extend(["low-protein", "low-phosphorus", "fluid-controlled"])
            elif "obesity" in disease.lower():
                considerations["special_needs"].extend(["calorie-controlled", "high-fiber", "portion-controlled"])
        
        # Remove duplicates
        considerations["special_needs"] = list(set(considerations["special_needs"]))
        
        return considerations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary for easy serialization"""
        return {
            "age": self.age,
            "weight": self.weight,
            "nationality": self.nationality,
            "diseases": self.diseases,
            "food_habit": self.food_habit,
            "bmi": self.get_bmi(),
            "age_category": self.get_age_category(),
            "dietary_considerations": self.get_dietary_considerations()
        }
    
    def __str__(self) -> str:
        """String representation of user profile"""
        diseases_str = ", ".join(self.diseases) if self.diseases != ["none"] else "None"
        return f"User Profile - Age: {self.age}, Weight: {self.weight}kg, Nationality: {self.nationality}, Food Habit: {self.food_habit.title()}, Health Conditions: {diseases_str}"


def create_user_profile_interactive() -> UserProfile:
    """
    Interactive function to create user profile from console input
    """
    print("=== Diet Plan Generator - User Profile ===")
    
    # Get age
    while True:
        try:
            age = int(input("Enter your age: "))
            break
        except ValueError:
            print("Please enter a valid age (number)")
    
    # Get weight
    while True:
        try:
            weight = float(input("Enter your weight in kg: "))
            break
        except ValueError:
            print("Please enter a valid weight (number)")
    
    # Get nationality
    print(f"\nSupported nationalities: {', '.join(VALIDATION_CONFIG['supported_nationalities'])}")
    nationality = input("Enter your nationality or cuisine preference: ").strip()
    
    # Get food habit
    print(f"\nFood habit options: {', '.join(DIET_CONFIG['food_habits'])}")
    food_habit = input("Enter your food habit preference (vegetarian/non-vegetarian/both): ").strip()
    if not food_habit:
        food_habit = "both"  # Default to both if no input
    
    # Get diseases
    print(f"\nCommon health conditions: {', '.join(DIET_CONFIG['common_diseases'])}")
    print("Enter your health conditions (separate multiple conditions with commas):")
    diseases_input = input("Health conditions (or 'none' if no conditions): ").strip()
    
    if diseases_input.lower() == "none" or diseases_input == "":
        diseases = ["none"]
    else:
        diseases = [disease.strip() for disease in diseases_input.split(",")]
    
    try:
        profile = UserProfile(age, weight, nationality, diseases, food_habit)
        print(f"\n✓ Profile created successfully!")
        print(profile)
        return profile
    except ValueError as e:
        print(f"Error creating profile: {e}")
        return create_user_profile_interactive()  # Retry


if __name__ == "__main__":
    # Test the UserProfile class
    print("Testing UserProfile class...")
    
    # Test valid profile
    try:
        profile = UserProfile(30, 70.5, "Indian", ["diabetes", "hypertension"], "vegetarian")
        print("✓ Valid profile created:", profile)
        print("Profile dict:", profile.to_dict())
    except Exception as e:
        print("✗ Error:", e)
    
    # Test interactive creation
    # profile = create_user_profile_interactive()