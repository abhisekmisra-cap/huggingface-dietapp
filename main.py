"""
Main application script for the Diet Plan Generator
Provides a user-friendly interface for generating personalized diet plans
"""
import sys
import os
from typing import Optional
import argparse

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_profile import UserProfile, create_user_profile_interactive
from diet_plan_generator import DietPlanGenerator
from config import MODEL_CONFIG, VALIDATION_CONFIG, DIET_CONFIG


def print_banner():
    """Print application banner"""
    print("=" * 60)
    print("         🍎 PERSONALIZED DIET PLAN GENERATOR 🥗")
    print("           Powered by Hugging Face LLMs")
    print("=" * 60)
    print()


def print_menu():
    """Print main menu options"""
    print("\n📋 What would you like to do?")
    print("1. Create new diet plan (interactive)")
    print("2. Create diet plan with custom parameters")
    print("3. View supported options")
    print("4. Exit")
    print("-" * 40)


def print_supported_options():
    """Print all supported options for user reference"""
    print("\n📊 SUPPORTED OPTIONS:")
    print("\n🌍 Supported Nationalities/Cuisines:")
    for nationality in VALIDATION_CONFIG["supported_nationalities"]:
        print(f"   • {nationality}")
    
    print("\n�️ Food Habit Options:")
    from config import DIET_CONFIG
    for habit in DIET_CONFIG["food_habits"]:
        print(f"   • {habit.title()}")
    
    print("\n🏥 Common Health Conditions:")
    for condition in DIET_CONFIG["common_diseases"]:
        print(f"   • {condition.title()}")
    
    print(f"\n📏 Age Range: {VALIDATION_CONFIG['age_range'][0]} - {VALIDATION_CONFIG['age_range'][1]} years")
    print(f"⚖️  Weight Range: {VALIDATION_CONFIG['weight_range'][0]} - {VALIDATION_CONFIG['weight_range'][1]} kg")


def create_custom_profile() -> Optional[UserProfile]:
    """Create user profile with custom parameters"""
    print("\n📝 Create Custom Profile")
    print("Enter the following information:")
    
    try:
        # Age input
        age_input = input(f"Age ({VALIDATION_CONFIG['age_range'][0]}-{VALIDATION_CONFIG['age_range'][1]}): ").strip()
        age = int(age_input)
        
        # Weight input
        weight_input = input(f"Weight in kg ({VALIDATION_CONFIG['weight_range'][0]}-{VALIDATION_CONFIG['weight_range'][1]}): ").strip()
        weight = float(weight_input)
        
        # Nationality input
        print(f"\nSupported nationalities: {', '.join(VALIDATION_CONFIG['supported_nationalities'][:5])}... (and more)")
        nationality = input("Nationality/Cuisine preference: ").strip()
        
        # Food habit input
        print(f"\nFood habit options: {', '.join(DIET_CONFIG['food_habits'])}")
        food_habit = input("Food habit preference (vegetarian/non-vegetarian/both): ").strip()
        if not food_habit:
            food_habit = "both"  # Default to both
        
        # Diseases input
        print("\nHealth conditions (separate multiple with commas, or 'none'):")
        diseases_input = input("Conditions: ").strip()
        
        if diseases_input.lower() in ['none', '']:
            diseases = ["none"]
        else:
            diseases = [d.strip() for d in diseases_input.split(',')]
        
        # Create profile
        profile = UserProfile(age, weight, nationality, diseases, food_habit)
        
        print(f"\n✅ Profile created successfully!")
        print(f"📋 {profile}")
        
        return profile
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        return None
    except KeyboardInterrupt:
        print("\n🚫 Profile creation cancelled.")
        return None


def generate_and_display_plan(generator: DietPlanGenerator, profile: UserProfile):
    """Generate and display diet plan"""
    print("\n🔄 Generating your personalized diet plan...")
    print("⏳ This may take a moment...")
    
    try:
        # Generate the diet plan
        diet_plan = generator.generate_diet_plan(profile)
        
        # Display the result
        print("\n" + "=" * 60)
        print("           🎉 YOUR PERSONALIZED DIET PLAN")
        print("=" * 60)
        print(f"\n👤 Profile: {profile}")
        print(f"🤖 Model: {generator.model_name}")
        print("\n" + "-" * 60)
        print(diet_plan)
        print("-" * 60)
        
        # Ask if user wants to save
        save_choice = input("\n💾 Would you like to save this diet plan to a file? (y/n): ").strip().lower()
        if save_choice in ['y', 'yes']:
            filename = input("📁 Enter filename (press Enter for default): ").strip()
            if not filename:
                filename = None
            
            generator.save_diet_plan(diet_plan, profile, filename)
        
        return True
        
    except Exception as e:
        print(f"❌ Error generating diet plan: {e}")
        return False


def main():
    """Main application function"""
    print_banner()
    
    # Initialize the generator (this connects to API)
    print("🔄 Connecting to Hugging Face API...")
    print("⚠️  Note: Hugging Face API token is required!")
    print("🔗 Get your free token at: https://huggingface.co/settings/tokens")
    
    try:
        generator = DietPlanGenerator()
    except Exception as e:
        print(f"❌ Failed to connect to API: {e}")
        print("Please get a Hugging Face API token and set HUGGINGFACE_API_TOKEN environment variable.")
        return
    
    print("✅ Model loaded successfully!")
    
    # Main application loop
    while True:
        print_menu()
        
        try:
            choice = input("Enter your choice (1-4): ").strip()
            
            if choice == '1':
                # Interactive profile creation
                print("\n🎯 Interactive Profile Creation")
                profile = create_user_profile_interactive()
                if profile:
                    generate_and_display_plan(generator, profile)
            
            elif choice == '2':
                # Custom profile creation
                profile = create_custom_profile()
                if profile:
                    generate_and_display_plan(generator, profile)
            
            elif choice == '3':
                # Show supported options
                print_supported_options()
            
            elif choice == '4':
                # Exit
                print("\n👋 Thank you for using Diet Plan Generator!")
                print("💡 Remember: Always consult healthcare professionals for medical advice.")
                break
            
            else:
                print("❌ Invalid choice. Please select 1-4.")
        
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {e}")
            continue


def command_line_interface():
    """Command line interface for the application"""
    parser = argparse.ArgumentParser(
        description="Generate personalized diet plans using Hugging Face API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --age 30 --weight 70 --nationality Indian --diseases diabetes,hypertension
  python main.py --interactive
  python main.py --help-options
  python main.py --token YOUR_HF_TOKEN --age 25 --weight 60 --nationality American
        """
    )
    
    parser.add_argument('--age', type=int, help='Age in years')
    parser.add_argument('--weight', type=float, help='Weight in kg')
    parser.add_argument('--nationality', type=str, help='Nationality or cuisine preference')
    parser.add_argument('--diseases', type=str, help='Health conditions (comma-separated)')
    parser.add_argument('--interactive', action='store_true', help='Use interactive mode')
    parser.add_argument('--help-options', action='store_true', help='Show supported options')
    parser.add_argument('--model', type=str, help='Hugging Face model name to use')
    parser.add_argument('--save', type=str, help='Save diet plan to specified file')
    parser.add_argument('--token', type=str, help='Hugging Face API token for better performance')
    
    args = parser.parse_args()
    
    # Handle help options
    if args.help_options:
        print_supported_options()
        return
    
    # Handle interactive mode or no arguments
    if args.interactive or not any([args.age, args.weight, args.nationality, args.diseases]):
        main()
        return
    
    # Handle command line arguments
    if not all([args.age, args.weight, args.nationality]):
        print("❌ Error: --age, --weight, and --nationality are required for non-interactive mode")
        parser.print_help()
        return
    
    try:
        # Parse diseases
        if args.diseases:
            diseases = [d.strip() for d in args.diseases.split(',')]
        else:
            diseases = ["none"]
        
        # Create profile
        profile = UserProfile(args.age, args.weight, args.nationality, diseases)
        print(f"✅ Profile: {profile}")
        
        # Initialize generator
        print("🔄 Connecting to Hugging Face API...")
        model_name = args.model if args.model else None
        api_token = args.token if args.token else None
        generator = DietPlanGenerator(model_name=model_name, api_token=api_token)
        
        # Generate plan
        print("🔄 Generating diet plan...")
        diet_plan = generator.generate_diet_plan(profile)
        
        # Display result
        print("\n" + "=" * 60)
        print("           🎉 YOUR PERSONALIZED DIET PLAN")
        print("=" * 60)
        print(diet_plan)
        print("=" * 60)
        
        # Save if requested
        if args.save:
            generator.save_diet_plan(diet_plan, profile, args.save)
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Command line mode
        command_line_interface()
    else:
        # Interactive mode
        main()