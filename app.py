"""
Flask Web Interface for Diet Plan Generator
"""
import os
import sys
from flask import Flask, render_template, request, flash, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, SelectField, SelectMultipleField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length
from wtforms.widgets import CheckboxInput, ListWidget

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from user_profile import UserProfile
from diet_plan_generator import DietPlanGenerator
from config import VALIDATION_CONFIG, DIET_CONFIG

app = Flask(__name__)

# Configuration for Azure Web App
app.config.update(
    SECRET_KEY=os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production'),
    WTF_CSRF_ENABLED=True,
    WTF_CSRF_TIME_LIMIT=None,  # No time limit for CSRF tokens
    SEND_FILE_MAX_AGE_DEFAULT=31536000,  # Cache static files for 1 year
)

# Set debug mode based on environment
app.debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

class MultiCheckboxField(SelectMultipleField):
    """Custom field for multiple checkboxes"""
    widget = ListWidget(prefix_label=False)
    option_widget = CheckboxInput()

class DietPlanForm(FlaskForm):
    """Form for collecting user diet plan information"""
    age = IntegerField(
        'Age', 
        validators=[
            DataRequired(), 
            NumberRange(min=VALIDATION_CONFIG["age_range"][0], max=VALIDATION_CONFIG["age_range"][1])
        ]
    )
    
    weight = FloatField(
        'Weight (kg)', 
        validators=[
            DataRequired(), 
            NumberRange(min=VALIDATION_CONFIG["weight_range"][0], max=VALIDATION_CONFIG["weight_range"][1])
        ]
    )
    
    nationality = SelectField(
        'Nationality/Cuisine Preference',
        choices=[(nat, nat) for nat in VALIDATION_CONFIG["supported_nationalities"]], 
        validators=[DataRequired()]
    )
    
    food_habit = SelectField(
        'Food Habit',
        choices=[(habit, habit.title()) for habit in DIET_CONFIG["food_habits"]],
        validators=[DataRequired()],
        default="both"
    )
    
    diseases = MultiCheckboxField(
        'Health Conditions',
        choices=[(disease, disease.title()) for disease in DIET_CONFIG["common_diseases"]],
        coerce=str
    )
    
    api_token = StringField(
        'Hugging Face API Token (Optional)',
        validators=[Length(max=200)]
    )
    
    submit = SubmitField('Generate Diet Plan')

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page with form"""
    form = DietPlanForm()
    
    if form.validate_on_submit():
        try:
            # Create user profile
            diseases = form.diseases.data if form.diseases.data else ["none"]
            profile = UserProfile(
                age=form.age.data,
                weight=form.weight.data,
                nationality=form.nationality.data,
                diseases=diseases,
                food_habit=form.food_habit.data
            )
            
            # Store form data in session
            session['profile_data'] = {
                'age': form.age.data,
                'weight': form.weight.data,
                'nationality': form.nationality.data,
                'diseases': diseases,
                'food_habit': form.food_habit.data,
                'api_token': form.api_token.data
            }
            
            return redirect(url_for('generate_plan'))
            
        except ValueError as e:
            flash(f'Error creating profile: {e}', 'error')
        except Exception as e:
            flash(f'Unexpected error: {e}', 'error')
    
    return render_template('index.html', form=form)

@app.route('/generate')
def generate_plan():
    """Generate and display diet plan"""
    if 'profile_data' not in session:
        flash('Please fill out the form first', 'error')
        return redirect(url_for('index'))
    
    data = session['profile_data']
    
    try:
        # Recreate profile
        profile = UserProfile(
            age=data['age'],
            weight=data['weight'],
            nationality=data['nationality'],
            diseases=data['diseases'],
            food_habit=data.get('food_habit', 'both')
        )
        
        # Initialize generator
        api_token = data.get('api_token') or os.getenv('HUGGINGFACE_API_TOKEN')
        generator = DietPlanGenerator(api_token=api_token)
        
        # Generate diet plan
        diet_plan = generator.generate_diet_plan(profile)
        
        return render_template('result.html', 
                             profile=profile, 
                             diet_plan=diet_plan,
                             dietary_considerations=profile.get_dietary_considerations())
        
    except Exception as e:
        flash(f'Error generating diet plan: {e}', 'error')
        return redirect(url_for('index'))

@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@app.route('/setup')
def setup():
    """Setup guide page"""
    return render_template('setup.html')

if __name__ == '__main__':
    # Create directories if they don't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Get port from environment variable for Azure
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    
    print("🚀 Starting Diet Plan Generator Web Interface...")
    print(f"🌐 Server will run on port: {port}")
    if not debug_mode:
        print("🔒 Running in production mode")
    print("⚠️  Note: Hugging Face API token is recommended for best performance")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)