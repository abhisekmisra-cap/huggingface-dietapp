# 🍎 Personalized Diet Plan Generator

**Developed by:** Dr. Abhishek Mishra  
**Powered by:** Hugging Face LLMs  
**Purpose:** Experimentation & Learning  

A Python application that uses Hugging Face Inference API to generate personalized diet plans based on user's age, weight, nationality, and health conditions. No local model downloads required!

## ✨ Features

- **🌐 Web Interface**: Beautiful, responsive web interface with Bootstrap styling
- **API-Powered**: Uses Hugging Face Inference API - no local model downloads needed!
- **Personalized**: Considers age, weight, nationality, and health conditions
- **Health-Aware**: Provides specialized recommendations for various health conditions
- **Cultural Adaptation**: Incorporates cuisine preferences based on nationality
- **Multiple Interfaces**: Web interface, interactive console, and command-line
- **Flexible Models**: Supports various Hugging Face models via API
- **Fast Setup**: No large model downloads, works immediately
- **Print-Friendly**: Web interface includes print-optimized styling
- **Mobile-Responsive**: Works perfectly on phones, tablets, and desktops

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Internet connection (for API calls)
- **Required**: Hugging Face API token (free)

### Installation

1. **Clone or download this repository**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Get Hugging Face API Token (Required):**
   - Go to [Hugging Face Tokens](https://huggingface.co/settings/tokens)
   - Create a new token (read access is sufficient) - **It's FREE!**
   - Set environment variable: `set HUGGINGFACE_API_TOKEN=your_token_here` (Windows)
   - Or use `--token your_token_here` in command line

4. **Get help with API token setup:**
   ```bash
   python get_token.py
   ```

## 🌐 **Web Interface (Recommended)**

### Option 1: Quick Start Scripts
```bash
# Windows
start_web.bat

# Linux/Mac
./start_web.sh
```

### Option 2: Manual Start
```bash
python app.py
```
Then open `http://localhost:5000` in your browser.

### Web Features:
- **🎨 Beautiful Interface**: Modern, responsive design with Bootstrap
- **📱 Mobile-Friendly**: Works perfectly on phones and tablets
- **🔄 Real-time Validation**: Form validation with helpful error messages
- **📊 Visual Profile**: Clear display of your health profile and BMI
- **🖨️ Print-Friendly**: Optimized for printing diet plans
- **🔒 Secure**: Data processed locally, API tokens not stored
- **💡 Guided Setup**: Built-in setup guide for API tokens

## 💻 **Command Line Interface**

### Interactive Mode
```bash
python main.py
```

### Direct Command
```bash
python main.py --age 30 --weight 70 --nationality Indian --diseases diabetes,hypertension
```

## 📊 Usage Examples

### Web Interface (Recommended)
```bash
python app.py
```
Open your browser and go to `http://localhost:5000` for a user-friendly web interface.

### Interactive Mode
```bash
python main.py
```
Follow the interactive prompts to create your profile and generate a diet plan.

### Command Line Mode
```bash
# Basic usage
python main.py --age 30 --weight 70 --nationality Indian --diseases diabetes,hypertension

# Save to specific file
python main.py --age 25 --weight 65 --nationality American --diseases none --save my_diet_plan.txt

# Use custom model
python main.py --age 35 --weight 80 --nationality Italian --diseases "heart disease" --model gpt2

# With API token for better performance
python main.py --token YOUR_API_TOKEN --age 30 --weight 70 --nationality Indian
```

### Programmatic Usage
```python
from user_profile import UserProfile
from diet_plan_generator import DietPlanGenerator

# Create user profile
profile = UserProfile(
    age=30,
    weight=70.0,
    nationality="Indian",
    diseases=["diabetes", "hypertension"]
)

# Generate diet plan (with optional API token)
generator = DietPlanGenerator(api_token="your_token_here")  # or None for no token
diet_plan = generator.generate_diet_plan(profile)
print(diet_plan)
```

## 📁 File Structure

```
Huggingface-Dietapp/
├── app.py                     # Web interface (Flask)
├── main.py                    # Command-line application  
├── diet_plan_generator.py     # Core AI API integration
├── user_profile.py           # User input handling and validation
├── config.py                 # Configuration settings
├── get_token.py              # Helper to get API token
├── requirements.txt          # Python dependencies
├── startup.py                # Azure Web App startup script
├── azure_config.py           # Azure-specific configuration
├── start_web.bat             # Windows local startup
├── start_web.sh              # Linux/Mac local startup
├── deploy_azure.bat          # Windows Azure deployment
├── deploy_azure.sh           # Linux/Mac Azure deployment
├── deploy_simple.bat         # Simplified Azure deployment
├── AZURE_DEPLOYMENT.md       # Azure deployment guide
├── templates/                # Web interface templates
│   ├── base.html             # Base template with styling
│   ├── index.html            # Main form page
│   ├── result.html           # Diet plan results
│   ├── about.html            # About page
│   └── setup.html            # Setup instructions
└── README.md                # This file
```

## ⚙️ Configuration

Edit `config.py` to customize:

- **Model Selection**: Change the Hugging Face model used
- **Generation Parameters**: Adjust temperature, max tokens, etc.
- **Supported Options**: Add new nationalities or health conditions
- **Prompt Templates**: Customize the AI prompts

### Available Models
- `microsoft/DialoGPT-medium` (default)
- `microsoft/DialoGPT-small` (faster)
- `gpt2` (fallback)
- Any compatible Hugging Face model

## 🏥 Supported Health Conditions

- Diabetes
- Hypertension (High Blood Pressure)
- Heart Disease
- Obesity
- High Cholesterol
- Kidney Disease
- Celiac Disease
- Food Allergies
- None (healthy individuals)

## 🌍 Supported Nationalities/Cuisines

- American
- Indian
- Chinese
- Japanese
- Italian
- Mexican
- French
- German
- British
- Mediterranean
- Middle Eastern
- African
- Other

## 🧪 Testing

### Test Web Interface
1. Run `python app.py` or `start_web.bat`
2. Open `http://localhost:5000`
3. Fill out the form and generate a diet plan

### Test Command Line
```bash
# Get help setting up API token
python get_token.py

# Test the application
python main.py --age 30 --weight 70 --nationality Indian --diseases none
```

## 🌐 Web Interface Screenshots

The web interface provides:

1. **Home Page**: Clean form for entering your profile information
2. **Results Page**: Beautiful display of your personalized diet plan
3. **About Page**: Information about the application and its features
4. **Setup Guide**: Step-by-step instructions for getting your API token

### Navigation Features:
- Responsive navigation bar
- Mobile-optimized design
- Form validation with error messages
- Print button for diet plans
- Link to setup guide for API tokens

## ☁️ Azure Web App Deployment

Deploy your application to Azure Web App for global access and professional hosting:

### 🚀 Quick Deploy

**Windows:**
```bash
deploy_azure.bat
```

**Linux/Mac:**
```bash
chmod +x deploy_azure.sh
./deploy_azure.sh
```

### 📋 Prerequisites
- Azure account (free tier available)
- Hugging Face API token
- Git installed
- Azure CLI installed

### 📖 Detailed Guide
See **[AZURE_DEPLOYMENT.md](AZURE_DEPLOYMENT.md)** for comprehensive deployment instructions.

### 🌐 After Deployment
- Your app will be available at: `https://your-app-name.azurewebsites.net`
- Automatic HTTPS and scaling included
- Monitor usage in Azure Portal
- Free tier: 1GB storage, perfect for learning

### 🔧 Azure Deployment Files
- `startup.py` - Azure Web App startup script
- `azure_config.py` - Azure-specific environment settings
- `deploy_azure.bat/sh` - Complete deployment automation
- `deploy_simple.bat` - Streamlined deployment script
- `AZURE_DEPLOYMENT.md` - Comprehensive deployment guide

## 🔧 Troubleshooting

### Common Issues

1. **Model Download Fails**
   - Ensure stable internet connection
   - Check available disk space (models can be 1-3GB)
   - Try using a smaller model in `config.py`

2. **Out of Memory**
   - Use CPU instead of GPU: Set device to "cpu" in config
   - Try smaller models like `microsoft/DialoGPT-small`
   - Reduce `max_length` in configuration

3. **Import Errors**
   - Reinstall dependencies: `pip install -r requirements.txt --upgrade`
   - Check Python version compatibility

4. **Poor Diet Plan Quality**
   - Try different models in `config.py`
   - Adjust temperature and other generation parameters
   - Provide more specific health condition details

### Performance Optimization

- **GPU Acceleration**: Install PyTorch with CUDA support for faster generation
- **Model Caching**: Models are cached after first download
- **Batch Processing**: Use `examples.py` for generating multiple plans efficiently

## 📝 Example Output

```
=== PERSONALIZED DIET PLAN ===

Profile Summary:
- Age: 30 years (adult)
- Weight: 70.0 kg (BMI: 24.2)
- Cuisine Preference: Indian
- Health Conditions: diabetes, hypertension

DAILY MEAL PLAN:

BREAKFAST:
- Oats upma with vegetables and a small amount of ghee
- Herbal tea or green tea
- A small portion of nuts (almonds or walnuts)

LUNCH:
- Brown rice or quinoa (1 cup)
- Dal (lentils) with minimal oil
- Mixed vegetable curry
- Small portion of yogurt
- Salad with cucumber and tomatoes

DINNER:
- Roti made from whole wheat (1-2 pieces)
- Grilled or steamed fish/chicken/paneer
- Steamed vegetables
- Small bowl of clear soup

SNACKS:
- Fresh fruits (apple, guava, or berries)
- Roasted chickpeas
- Herbal tea

SPECIAL CONSIDERATIONS:
- Monitor blood sugar levels regularly
- Limit sodium intake for blood pressure management
- Include fiber-rich foods for better glucose control
- Stay hydrated with 8-10 glasses of water daily
```

## 🤝 Contributing

Feel free to contribute by:
- Adding new model support
- Improving prompt templates
- Adding more health conditions
- Enhancing the user interface
- Adding new cuisine types

## ⚠️ Disclaimer

This application generates AI-based dietary suggestions for informational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult with qualified healthcare providers before making significant dietary changes, especially if you have medical conditions.

## 📄 License

This project is provided as-is for educational and personal use. Please respect Hugging Face's model licenses and terms of use.

## ⚠️ Important Disclaimer

This application is developed for **experimentation and learning purposes only**. 

- **Educational Use**: This tool is designed for learning about AI and diet planning concepts
- **Not Medical Advice**: Diet plans generated are AI-generated suggestions, not professional medical advice
- **Consult Professionals**: Always consult with healthcare professionals, nutritionists, or dietitians for personalized medical and dietary advice
- **Research & Experimentation**: Use this tool to explore AI capabilities and learn about nutrition concepts

## 🔗 Resources

- [Hugging Face Transformers](https://huggingface.co/transformers/)
- [Hugging Face Inference API](https://huggingface.co/docs/api-inference/)
- [Flask Web Framework](https://flask.palletsprojects.com/)

---

**Developed by:** Dr. Abhishek Mishra  
**Powered by:** Hugging Face Large Language Models  
**Purpose:** Experimentation & Learning  

Made with ❤️ for educational purposes