from flask import Flask, render_template, request
import requests
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# IMPORTANT: Replace with your actual OpenWeatherMap API key
# It's recommended to store API keys in environment variables for production
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "836b9dd9d83e8f864c9ad1c0c9e375a6") 

# API Endpoints
CURRENT_WEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast" # This is for the 5-day / 3-hour forecast

@app.route('/', methods=['GET', 'POST'])
def index():
    current_weather_data = None
    forecast_data = [] # This list will hold our processed daily forecast
    error_message = None

    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            # Step 1: Get city coordinates (latitude and longitude)
            # The 5-day forecast API works better with lat/lon
            # So, we first use the current weather API to get the coordinates
            geo_params = {
                'q': city,
                'appid': OPENWEATHER_API_KEY
            }
            try:
                geo_response = requests.get(CURRENT_WEATHER_URL, params=geo_params)
                geo_response.raise_for_status() # Raise an exception for HTTP errors
                geo_data = geo_response.json()

                if geo_data.get("cod") == 200:
                    lat = geo_data['coord']['lat']
                    lon = geo_data['coord']['lon']
                    city_name = geo_data['name'] # Use the city name returned by the API for consistency

                    # Step 2: Get 5-day / 3-hour forecast using coordinates
                    forecast_params = {
                        'lat': lat,
                        'lon': lon,
                        'appid': OPENWEATHER_API_KEY,
                        'units': 'metric'  # or 'imperial' for Fahrenheit
                    }
                    forecast_response = requests.get(FORECAST_URL, params=forecast_params)
                    forecast_response.raise_for_status()
                    forecast_raw_data = forecast_response.json()

                    if forecast_raw_data.get("cod") == "200":
                        # Process forecast data to group by day
                        daily_forecast = {}
                        for item in forecast_raw_data['list']:
                            timestamp = item['dt']
                            dt_object = datetime.fromtimestamp(timestamp)
                            # We want to group by date (YYYY-MM-DD)
                            date_key = dt_object.strftime('%Y-%m-%d')

                            if date_key not in daily_forecast:
                                # Initialize data for a new day
                                daily_forecast[date_key] = {
                                    'date': dt_object.strftime('%A, %B %d'), # E.g., 'Monday, May 27'
                                    'temps': [],
                                    'descriptions': [],
                                    'icons': []
                                }
                            
                            # Add data for the current 3-hour interval to the respective day
                            daily_forecast[date_key]['temps'].append(item['main']['temp'])
                            daily_forecast[date_key]['descriptions'].append(item['weather'][0]['description'])
                            daily_forecast[date_key]['icons'].append(item['weather'][0]['icon'])
                        
                        # Calculate daily averages/representative values
                        # Iterate through the collected daily data
                        for date_key, data in daily_forecast.items():
                            # Calculate average temperature for the day
                            avg_temp = sum(data['temps']) / len(data['temps'])
                            
                            # For description and icon, a simplistic approach is to take the most frequent
                            # or just the first one of the day. More sophisticated logic could choose
                            # the dominant weather condition for the day.
                            description = max(set(data['descriptions']), key=data['descriptions'].count)
                            icon = data['icons'][0] # Take the icon from the first forecast entry for the day

                            forecast_data.append({
                                'date': data['date'],
                                'temperature': round(avg_temp, 1), # Round to one decimal place
                                'description': description,
                                'icon': icon
                            })
                        
                        # Sort forecast by date to ensure correct order
                        # This handles cases where API might not return perfectly sorted or for robustness
                        forecast_data.sort(key=lambda x: datetime.strptime(x['date'], '%A, %B %d'))

                        # Also get current weather for the entered city
                        # (We already have this from the initial geo_data call)
                        current_weather_data = {
                            'city': geo_data['name'],
                            'temperature': geo_data['main']['temp'],
                            'description': geo_data['weather'][0]['description'],
                            'icon': geo_data['weather'][0]['icon'],
                            'humidity': geo_data['main']['humidity'],
                            'wind_speed': geo_data['wind']['speed']
                        }

                    else:
                        error_message = f"Could not retrieve forecast for {city_name}. Please try again."

                else:
                    error_message = f"City not found: {city}. Please try again."

            except requests.exceptions.RequestException as e:
                error_message = f"Error fetching weather data: {e}. Please check your internet connection or API key."
            except Exception as e:
                error_message = f"An unexpected error occurred: {e}"
        else:
            error_message = "Please enter a city name."

    # Pass both current weather and forecast data to the template
    return render_template('index.html', current_weather=current_weather_data, forecast=forecast_data, error=error_message)

if __name__ == '__main__':
    app.run(debug=True) # debug=True is good for development