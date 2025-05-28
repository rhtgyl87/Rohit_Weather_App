from flask import Flask, render_template, request
import requests
import os
from datetime import datetime

app = Flask(__name__)

# IMPORTANT: Replace with your actual Visual Crossing API key
# It's recommended to store API keys in environment variables for production
VISUALCROSSING_API_KEY = os.environ.get("VISUALCROSSING_API_KEY", "YOUR_VC_API_KEY")

# Visual Crossing Weather API Base URL
# The location (city) will be appended to this URL path
VISUALCROSSING_BASE_URL = "https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline"

@app.route('/', methods=['GET', 'POST'])
def index():
    current_weather_data = None
    forecast_data = []
    error_message = None

    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            # Construct the API URL for the specific city
            # Visual Crossing integrates the city directly into the URL path
            api_url = f"{VISUALCROSSING_BASE_URL}/{city}"

            params = {
                'key': '6XQJPZTR34ZXRAS294NMBTW8R',
                'unitGroup': 'metric', # Use 'us' for Fahrenheit
                'include': 'current,days', # Request current conditions and daily forecast
                'contentType': 'json'
            }
            try:
                response = requests.get(api_url, params=params)
                response.raise_for_status() # Raise an exception for HTTP errors
                data = response.json()

                # Visual Crossing provides 'resolvedAddress' which is the best match for the query
                # Use this for the city name in the display.
                display_city_name = data.get('resolvedAddress', city)

                # Parse current weather data from 'currentConditions'
                if 'currentConditions' in data:
                    current = data['currentConditions']
                    current_weather_data = {
                        'city': display_city_name,
                        'temperature': current.get('temp'),
                        'conditions': current.get('conditions'), # New field name for description
                        'icon': current.get('icon'), # Icon string (e.g., 'partly-cloudy-day')
                        'humidity': current.get('humidity'),
                        'wind_speed': current.get('windspeed') # Wind speed in km/h if metric
                    }

                # Parse 5-day forecast data from 'days' array
                # The 'days' array includes today (index 0) and subsequent days.
                # We want the next 5 days, so we iterate through the first 6 elements
                # (today + next 5 days) and potentially skip index 0 in display.
                # Or, for strict "5-day forecast" not including today's specific summary,
                # we can start from index 1. Let's aim for 5 distinct forecast days.
                for i, day_item in enumerate(data.get('days', [])):
                    if i > 5: # Limit to 5 days, starting from the current day (index 0)
                        break
                    
                    # Convert epoch timestamp to datetime object
                    dt_object = datetime.fromtimestamp(day_item['datetimeEpoch'])
                    forecast_data.append({
                        'date': dt_object.strftime('%A, %B %d'),
                        'temperature_min': day_item.get('tempmin'),
                        'temperature_max': day_item.get('tempmax'),
                        'conditions': day_item.get('conditions'), # New field name for description
                        'icon': day_item.get('icon') # Icon string
                    })

            except requests.exceptions.RequestException as e:
                error_message = f"Error fetching weather data: {e}. Please check your internet connection or API key."
            except Exception as e:
                error_message = f"An unexpected error occurred: {e}"
        else:
            error_message = "Please enter a city name."

    return render_template('index.html', current_weather=current_weather_data, forecast=forecast_data, error=error_message)

if __name__ == '__main__':
    app.run(debug=True)