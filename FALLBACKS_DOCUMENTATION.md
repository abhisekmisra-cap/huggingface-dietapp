# Fallbacks Documentation

This document describes all fallback mechanisms used in the Diet Plan Generator application.

## 1. **Height Field**
- **Added**: Height field now captured in **inches**
- **Location**: Form (`app.py`), UserProfile (`user_profile.py`)
- **Validation**: Must be between 36-96 inches (3-8 feet)
- **Usage**: Used to calculate BMI for better personalization
- **Display**: Shown in both inches and meters in the output

---

## 2. **API Connection Fallbacks**

### 2.1 API Token Fallback
- **Location**: `app.py` - `generate_plan()` route
- **Code**: 
  ```python
  api_token = data.get('api_token') or os.getenv('HUGGINGFACE_API_TOKEN')
  ```
- **Behavior**: If user doesn't provide API token in form, use environment variable from `.env` file
- **Fallback Chain**: User Input → .env file → Error if both missing

### 2.2 API Test Failure Handling
- **Location**: `diet_plan_generator.py` - `__init__()` method
- **Code**:
  ```python
  test_result = self._test_api_connection()
  if test_result:
      print("✅ API connection successful!")
  else:
      print("⚠️  API test had issues, but will try during generation...")
  ```
- **Behavior**: Even if API test fails (404), app continues and tries during actual generation
- **Reason**: API test might fail due to cold start, but actual generation could succeed

### 2.3 API Method Fallback
- **Location**: `diet_plan_generator.py` - `_call_api()` method
- **Code**:
  ```python
  if "llama" in self.model_name.lower():
      return self._call_api_with_client(prompt, max_new_tokens)
  # Fallback to direct REST API for other models
  ```
- **Behavior**: 
  - Llama models → Use `InferenceClient.chat_completion()` (conversational task)
  - Other models → Use direct REST API (text-generation task)

---

## 3. **Meal Parsing Fallbacks**

### 3.1 Primary Meal Extraction
- **Location**: `diet_plan_generator.py` - `_format_output_as_table()` method
- **Behavior**: Parses LLM output by detecting keywords (BREAKFAST, LUNCH, DINNER, SNACKS)
- **Parsing Logic**: Looks for meal headers and extracts items below them

### 3.2 Fallback Meal Distribution
- **Location**: `diet_plan_generator.py` - Lines 291-304
- **Code**:
  ```python
  # FALLBACK: If parsing failed to extract meals, use raw text and distribute items
  if not any(meals.values()):
      all_lines = [l.strip() for l in generated_text.split('\n') if l.strip()]
      for i, line in enumerate(all_lines[:12]):
          # Distribute first 12 lines among meals
          if i < 3: meals['breakfast'].append(clean)
          elif i < 6: meals['lunch'].append(clean)
          elif i < 9: meals['dinner'].append(clean)
          else: meals['snacks'].append(clean)
  ```
- **Trigger**: When primary parsing fails (no meal sections detected)
- **Behavior**: Takes first 12 lines of LLM output and distributes them:
  - Lines 1-3 → Breakfast
  - Lines 4-6 → Lunch
  - Lines 7-9 → Dinner
  - Lines 10-12 → Snacks

### 3.3 Empty Meal Fallback Messages
- **Location**: `diet_plan_generator.py` - Lines 306-309
- **Code**:
  ```python
  breakfast_list = ... if meals['breakfast'] else '   • [No specific items - please try again]'
  lunch_list = ... if meals['lunch'] else '   • [No specific items - please try again]'
  dinner_list = ... if meals['dinner'] else '   • [No specific items - please try again]'
  snacks_list = ... if meals['snacks'] else '   • Fresh fruits, nuts, or healthy snacks (fallback)'
  ```
- **Trigger**: When a specific meal section has no items after all parsing attempts
- **Behavior**: Shows user-friendly message instead of empty section
- **Special Case**: Snacks shows generic healthy options as fallback

---

## 4. **Cuisine/Nationality Fallback**

### 4.1 Default Cuisine
- **Location**: `diet_plan_generator.py` - `_create_diet_prompt()` method
- **Code**:
  ```python
  cuisine_type = user_profile.nationality if user_profile.nationality else "Indian"
  ```
- **Trigger**: If nationality/cuisine is empty or None
- **Fallback**: Defaults to "Indian" cuisine

---

## 5. **Food Habit Fallback**

### 5.1 Default Food Preference
- **Location**: `app.py` - `generate_plan()` route
- **Code**:
  ```python
  food_habit=data.get('food_habit', 'both')  # Default to 'both' if not specified
  ```
- **Trigger**: If food_habit not in session data
- **Fallback**: Defaults to "both" (allows all food types)

---

## 6. **Error Handling Fallbacks**

### 6.1 API Error Messages
- **Location**: `diet_plan_generator.py` - `_call_api_with_client()` method
- **Behavior**: Provides helpful error messages based on error type:
  - **404 errors** → "Model not accessible" + instructions to accept license
  - **403 errors** → "Access denied" + link to model page
  - **Other errors** → Re-raises original error with context

### 6.2 Profile Creation Error Handling
- **Location**: `app.py` - `index()` route
- **Code**:
  ```python
  except ValueError as e:
      flash(f'Error creating profile: {e}', 'error')
  except Exception as e:
      flash(f'Unexpected error: {e}', 'error')
  ```
- **Behavior**: Catches validation errors and shows user-friendly messages

### 6.3 Generation Error Handling
- **Location**: `app.py` - `generate_plan()` route
- **Code**:
  ```python
  except Exception as e:
      flash(f'Error generating diet plan: {e}', 'error')
      return redirect(url_for('index'))
  ```
- **Behavior**: Redirects to home page with error message if generation fails

---

## 7. **Retry Mechanisms**

### 7.1 API Retry Logic
- **Location**: `diet_plan_generator.py` - `_call_api()` method
- **Configuration**: 3 retry attempts (configurable in `config.py`)
- **Retry Scenarios**:
  - **503 (Model loading)**: Wait 5-15 seconds and retry
  - **Timeout**: Retry immediately
  - **Other errors**: Wait 2 seconds and retry
- **Behavior**: After 3 failed attempts, raises exception

---

## Summary of All Fallbacks

| Component | Primary | Fallback 1 | Fallback 2 | Fallback 3 |
|-----------|---------|------------|------------|------------|
| **API Token** | User input | .env file | Error | - |
| **API Method** | InferenceClient (Llama) | REST API (others) | - | - |
| **Meal Parsing** | Keyword detection | Line distribution | Empty message | Generic items (snacks) |
| **Cuisine** | User selection | "Indian" default | - | - |
| **Food Habit** | User selection | "both" default | - | - |
| **Height** | User input (inches) | Validation error | - | - |
| **API Calls** | First attempt | Retry 1 (wait) | Retry 2 (wait) | Retry 3 → Error |

---

## Testing Fallbacks

To test fallbacks, try these scenarios:

1. **Empty API token**: Leave token blank → Should use .env token
2. **Bad LLM output**: Model returns unstructured text → Should distribute among meals
3. **API failure**: Network issues → Should retry 3 times
4. **Invalid height**: Enter 10 inches → Should show validation error
5. **No cuisine selected**: (Not possible with current form) → Would default to "Indian"

---

## Configuration

Fallback settings can be adjusted in `config.py`:
- `retry_attempts`: Number of API retry attempts (default: 3)
- `timeout_seconds`: API timeout before retry (default: 30)
- Height range: 36-96 inches (hardcoded in `user_profile.py`)
