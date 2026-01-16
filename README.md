# Training Recommendation Agent

A professional training plan generation agent built with Google ADK (Agent Development Kit). This agent collects user information through a progressive form, then generates a personalized weekly training plan based on user preferences, weather conditions, and geographical location.

## Features

- **Progressive Information Collection**: Dynamically collects user information (age, gender, fitness level, training goals, preferences, etc.) through an interactive form
- **Intelligent Training Plan Generation**: Creates a personalized 7-day training plan from the current day
- **Weather Integration**: Incorporates 1-week weather forecast using Google Weather API with automatic fallback to OpenWeatherMap API
- **Location-Based Recommendations**: Suggests nearby venues (parks, gyms, swimming pools, etc.) based on user's location and activity preferences
- **Gear Recommendations**: Provides appropriate attire and equipment suggestions based on the activity type
- **Customizable Configuration**: Form fields and information collection order are externalized into separate configuration files for easy modification

## Prerequisites

Before you begin, ensure you have the following installed:

1. **Python 3.10-3.12** (Python 3.13+ is not supported)
   ```bash
   python3 --version  # Should be 3.10, 3.11, or 3.12
   ```

2. **uv** (Python package manager)
   ```bash
   # Install uv if not already installed
   curl -LsSf https://astral.sh/uv/install.sh | sh
   # Or on macOS with Homebrew:
   brew install uv
   ```

3. **Google Cloud Project** with the following APIs enabled:
   - Generative Language API
   - Google Maps Platform APIs:
     - Maps JavaScript API
     - Geocoding API
     - Places API
     - Maps Embed API (for Weather API)

## Quick Start

### 1. Navigate to the Project Directory

```bash
cd python/agents/training-recommend
```

### 2. Install Dependencies

Install all required Python packages using `uv`:

```bash
uv sync
```

This will:
- Create a virtual environment (if not exists)
- Install all dependencies specified in `pyproject.toml`
- Generate/update `uv.lock` file

### 3. Configure Environment Variables

Create a `.env` file in the project root directory (`python/agents/training-recommend/.env`):

```bash
# Required: Google Cloud Configuration
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=1

# Optional: Google API Key (if not using service account authentication)
# GOOGLE_API_KEY=your-api-key

# Required: Google Maps API Key (for geocoding, places, and weather)
GOOGLE_MAPS_API_KEY=your-google-maps-api-key

# Optional: OpenWeatherMap API Key (fallback for weather data)
# If not provided, the agent will use mock data when Google Weather API fails
# OPENWEATHER_API_KEY=your-openweather-api-key
```

**How to get API keys:**

1. **Google Cloud Project ID**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one
   - Copy the Project ID

2. **Google API Key** (optional):
   - Go to [Google AI Studio](https://aistudio.google.com/apikey)
   - Click "Create API Key"
   - Copy the generated key

3. **Google Maps API Key**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
   - Click "Create Credentials" → "API Key"
   - Copy the generated key
   - **Important**: Restrict the API key to only the required APIs:
     - Maps JavaScript API
     - Geocoding API
     - Places API
     - Maps Embed API

4. **OpenWeatherMap API Key** (optional, for weather fallback):
   - Sign up at [OpenWeatherMap](https://openweathermap.org/api)
   - Go to API keys section
   - Copy your API key

### 4. Activate Virtual Environment (Optional)

If you want to use the virtual environment directly:

```bash
# On macOS/Linux:
source .venv/bin/activate

# On Windows:
.venv\Scripts\activate
```

### 5. Start the Backend Server

Start the FastAPI backend server:

```bash
# Method 1: Using uvicorn directly (if virtual environment is activated)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Method 2: Using uv run (recommended, no need to activate virtual environment)
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Method 3: Run the main.py file directly
uv run python app/main.py
```

The server will start on `http://localhost:8000`.

**Note**: The `--reload` flag enables auto-reload on code changes (useful for development). Remove it for production.

### 6. Access the Application

Open your browser and navigate to:

```
http://localhost:8000
```

You should see:
- The training recommendation agent interface
- An automatic welcome message
- A dynamic form that appears as the agent asks questions

## Usage

1. **Welcome Message**: When you open the page, the agent will automatically greet you with a welcome message.

2. **Progressive Form Collection**: The agent will ask questions one by one. As each question appears, a corresponding form field will be displayed:
   - **Basic Info**: Age (number), Gender (radio), Weight (number), Height (number)
   - **Health Information**: Injuries, Fitness Level (dropdown), Running Frequency
   - **Training Preferences**: Training Goals (multi-select), Training Days, Training Location (dropdown)
   - **Shoe Finder**: Arch Type (dropdown), Shoe Wear Pattern (dropdown), Shoe Feel (dropdown)
   - **Location**: City (with automatic geolocation support)

3. **Location Detection**: When asked about your location:
   - Click "Get Current Location" to automatically detect your location
   - The system will convert GPS coordinates to a detailed address
   - The city field will be auto-filled

4. **Submit Information**: After answering all questions, the agent will:
   - Fetch weather forecast for the next 7 days
   - Search for nearby training venues based on your preferences
   - Generate a personalized training plan
   - Display the plan in a structured JSON format (suitable for calendar rendering)

## Project Structure

```
training-recommend/
├── app/
│   └── main.py              # FastAPI backend server
├── static/
│   ├── index.html          # Frontend UI
│   └── form_config.js      # Form field configurations (externalized)
├── training_recommend/
│   ├── __init__.py
│   ├── agent.py            # ADK agent definition
│   ├── config.py            # Configuration management
│   ├── prompts.py          # Agent prompts and instructions
│   ├── collection_order.py # Information collection order (externalized)
│   └── tools/
│       ├── __init__.py
│       ├── weather.py      # Weather forecast tool (Google Weather API + OpenWeatherMap fallback)
│       ├── venues.py       # Nearby venues search tool (Google Places API)
│       └── gear.py         # Gear recommendation tool
├── pyproject.toml          # Project dependencies
├── uv.lock                 # Dependency lock file
└── README.md              # This file
```

## Configuration Files

### Form Field Configuration (`static/form_config.js`)

This file defines all form fields, their types, labels, placeholders, and validation rules. You can easily modify form fields without touching the main HTML file.

Example:
```javascript
const formFields = {
    age: {
        keywords: ['age', 'years old'],
        type: 'number',
        placeholder: 'Enter your age',
        label: 'Age',
        min: 10,
        max: 100
    },
    // ... more fields
};
```

### Information Collection Order (`training_recommend/collection_order.py`)

This file defines the order in which information is collected and the questions the agent asks. Modify `INFORMATION_COLLECTION_ORDER` to change the flow.

Example:
```python
INFORMATION_COLLECTION_ORDER = [
    {"field": "age", "question": "Please tell me your age, for example: 25"},
    {"field": "gender", "question": "Please tell me your gender (male/female)"},
    # ... more fields
]
```

## Troubleshooting

### 1. Module Not Found Errors

**Problem**: `ModuleNotFoundError: No module named 'training_recommend'`

**Solution**:
```bash
# Make sure you're in the project directory
cd python/agents/training-recommend

# Reinstall dependencies
uv sync
```

### 2. Environment Variables Not Loading

**Problem**: Environment variables are not being read from `.env` file

**Solution**:
- Ensure `.env` file exists in the project root (`python/agents/training-recommend/.env`)
- Check that the file format is correct (no spaces around `=`)
- Verify the file is not ignored by `.gitignore` (it should be)
- Restart the server after modifying `.env`

### 3. API Key Errors (403 PERMISSION_DENIED)

**Problem**: API key authentication fails

**Solution**:
- Verify API key is correct in `.env` file
- Check that the required APIs are enabled in Google Cloud Console
- For Google Maps API: Ensure the API key has the necessary restrictions and allowed APIs
- For Generative Language API: Ensure the API is enabled for your project

### 4. Weather API Returns 404 or "Location Not Supported"

**Problem**: Google Weather API doesn't support the location or returns an error

**Solution**:
- This is handled automatically by the fallback mechanism
- The agent will try OpenWeatherMap API if available
- If both fail, mock data will be used
- To enable OpenWeatherMap fallback, add `OPENWEATHER_API_KEY` to `.env`

### 5. Port Already in Use

**Problem**: Port 8000 is already in use

**Solution**:
```bash
# Use a different port
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001

# Or find and kill the process using port 8000
# On macOS/Linux:
lsof -ti:8000 | xargs kill -9

# On Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### 6. Frontend Not Loading or Form Fields Not Showing

**Problem**: The HTML page loads but forms don't appear

**Solution**:
- Check browser console for JavaScript errors
- Verify `form_config.js` is loading correctly
- Clear browser cache and hard refresh (Ctrl+Shift+R or Cmd+Shift+R)
- Check that the server is running and accessible

## Development

### Running in Development Mode

```bash
# Start server with auto-reload
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Adding New Form Fields

1. Add the field configuration to `static/form_config.js`
2. Add the field to `INFORMATION_COLLECTION_ORDER` in `training_recommend/collection_order.py`
3. Restart the server

### Modifying Agent Prompts

Edit `training_recommend/prompts.py` to modify agent behavior, instructions, or output format.

## License

Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
