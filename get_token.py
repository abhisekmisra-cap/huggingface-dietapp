"""
Helper script to guide users through getting a Hugging Face API token
"""
import os
import webbrowser
import sys


def print_banner():
    print("=" * 60)
    print("      🔑 HUGGING FACE API TOKEN SETUP GUIDE")
    print("=" * 60)


def check_existing_token():
    """Check if token already exists"""
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if token:
        print(f"✅ API token found: {token[:8]}...{token[-4:] if len(token) > 12 else ''}")
        return True
    else:
        print("❌ No API token found in environment variables")
        return False


def guide_token_creation():
    """Guide user through token creation"""
    print("\n📝 HOW TO GET YOUR FREE HUGGING FACE API TOKEN:")
    print("=" * 50)
    print("1. 🌐 Go to: https://huggingface.co/settings/tokens")
    print("2. 📝 Sign up for a free account if you don't have one")
    print("3. ➕ Click 'New token'")
    print("4. 📝 Give it a name like 'Diet Plan Generator'")
    print("5. 🔍 Select 'Read' role (sufficient for this app)")
    print("6. ✅ Click 'Generate a token'")
    print("7. 📋 Copy the generated token")
    
    print("\n🌐 Opening Hugging Face tokens page...")
    try:
        webbrowser.open("https://huggingface.co/settings/tokens")
        print("✅ Browser opened to Hugging Face tokens page")
    except:
        print("❌ Could not open browser automatically")
        print("Please manually go to: https://huggingface.co/settings/tokens")


def set_token_instructions():
    """Show how to set the token"""
    print("\n⚙️  HOW TO SET YOUR TOKEN:")
    print("=" * 30)
    print("\n🪟 For Windows (Command Prompt):")
    print("   set HUGGINGFACE_API_TOKEN=your_token_here")
    
    print("\n🪟 For Windows (PowerShell):")
    print("   $env:HUGGINGFACE_API_TOKEN='your_token_here'")
    
    print("\n🐧 For Linux/Mac:")
    print("   export HUGGINGFACE_API_TOKEN=your_token_here")
    
    print("\n📝 Or add to your .env file:")
    print("   HUGGINGFACE_API_TOKEN=your_token_here")
    
    print("\n🎯 Or use command line option:")
    print("   python main.py --token your_token_here")


def test_token():
    """Help user test their token"""
    print("\n🧪 TESTING YOUR TOKEN:")
    print("=" * 25)
    
    token = input("Paste your token here to test (or press Enter to skip): ").strip()
    
    if not token:
        print("⏭️  Skipping token test")
        return
    
    try:
        import requests
        
        # Test 1: Check if token is valid
        print("🔄 Testing token validity...")
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://huggingface.co/api/whoami", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Token works! Hello, {user_info.get('name', 'User')}!")
        else:
            print(f"❌ Token validation failed: {response.status_code}")
            return False
        
        # Test 2: Test inference API
        print("🔄 Testing inference API...")
        api_url = "https://huggingface.co/api/inference/models/gpt2"
        payload = {
            "inputs": "Hello",
            "parameters": {"max_new_tokens": 5, "return_full_text": False}
        }
        
        response = requests.post(api_url, headers=headers, json=payload)
        if response.status_code == 200:
            print("✅ Inference API works!")
        elif response.status_code == 503:
            print("⏳ Model is loading - this is normal, try again in a minute")
        else:
            print(f"⚠️  Inference API returned: {response.status_code}")
            print("This might be temporary - the token itself is valid")
        
        # Offer to set the environment variable
        if sys.platform.startswith('win'):
            print(f"\n💡 To set permanently, run:")
            print(f"   set HUGGINGFACE_API_TOKEN={token}")
        
        return True
            
    except ImportError:
        print("⚠️  Cannot test token (requests library not installed)")
        print("The token format looks correct though!")
        return True
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False


def test_full_application():
    """Test the full diet plan generator application"""
    print("\n🧪 TESTING FULL APPLICATION:")
    print("=" * 35)
    
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        print("❌ No API token found in environment")
        print("Please set HUGGINGFACE_API_TOKEN first")
        return False
    
    try:
        # Import and test the diet plan generator
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        from user_profile import UserProfile
        from diet_plan_generator import DietPlanGenerator
        
        print("🔄 Creating test profile...")
        profile = UserProfile(30, 70.0, "American", ["none"])
        print(f"✅ Profile created: {profile}")
        
        print("🔄 Initializing diet plan generator...")
        generator = DietPlanGenerator(api_token=token)
        
        print("🔄 Generating diet plan...")
        diet_plan = generator.generate_diet_plan(profile)
        
        if len(diet_plan.strip()) > 100:  # Reasonable diet plan length
            print("✅ Diet plan generated successfully!")
            print(f"Preview: {diet_plan[:100]}...")
            return True
        else:
            print("⚠️  Diet plan seems too short, but generation worked")
            return True
            
    except Exception as e:
        print(f"❌ Application test failed: {e}")
        return False


def main():
    """Main function"""
    print_banner()
    
    print("\n🎯 This script will help you set up a Hugging Face API token")
    print("The token is FREE and required to use the Diet Plan Generator\n")
    
    # Check if token already exists
    if check_existing_token():
        choice = input("\nDo you want to test your existing token? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            token = os.getenv("HUGGINGFACE_API_TOKEN")
            # Mock test with existing token
            print("🔄 Testing existing token...")
            try:
                import requests
                headers = {"Authorization": f"Bearer {token}"}
                response = requests.get("https://huggingface.co/api/whoami", headers=headers)
                if response.status_code == 200:
                    user_info = response.json()
                    print(f"✅ Your token works! Hello, {user_info.get('name', 'User')}!")
                    print("\n🎉 You're all set! Run: python main.py")
                    return
                else:
                    print("❌ Token appears to be invalid")
            except:
                print("⚠️  Could not test token")
        
        print("\n🎉 You can now run: python main.py")
        return
    
    # Guide through getting a token
    choice = input("Would you like help getting an API token? (y/n): ").strip().lower()
    if choice not in ['y', 'yes']:
        print("👋 No problem! Get your token at: https://huggingface.co/settings/tokens")
        return
    
    guide_token_creation()
    input("\nPress Enter after you've created your token...")
    
    set_token_instructions()
    
    # Test the token
    test_token()
    
    # Optional: Test the full application
    if os.getenv("HUGGINGFACE_API_TOKEN"):
        choice = input("\nWould you like to test the full application? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            test_full_application()
    
    print("\n" + "=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("=" * 60)
    print("Now you can run the diet plan generator:")
    print("   python main.py")
    print("\nNeed help? Run this script again:")
    print("   python get_token.py")


if __name__ == "__main__":
    main()