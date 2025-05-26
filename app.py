from flask import Flask, render_template, request
import requests
import os

app = Flask(__name__)

# Replace with your actual OpenWeatherMap API key
# It's recommended to store API keys in environment variables for production
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "YOUR_API_KEY")
OPENWEATHER_URL = "http://api.openweathermap.org/data/2.5/weather"
## changes
@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    error_message = None

    if request.method == 'POST':
        city = request.form.get('city')
        if city:
            params = {
                'q': city,
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric'  # or 'imperial' for Fahrenheit
            }
            try:
                response = requests.get(OPENWEATHER_URL, params=params)
                response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
                data = response.json()

                if data.get("cod") == 200:  # Check if the city was found
                    weather_data = {
                        'city': data['name'],
                        'temperature': data['main']['temp'],
                        'description': data['weather'][0]['description'],
                        'icon': data['weather'][0]['icon'],
                        'humidity': data['main']['humidity'],
                        'wind_speed': data['wind']['speed']
                    }
                else:
                    error_message = f"City not found: {city}. Please try again."
            except requests.exceptions.RequestException as e:
                error_message = f"Error fetching weather data: {e}. Please check your internet connection or API key."
            except Exception as e:
                error_message = f"An unexpected error occurred: {e}"
        else:
            error_message = "Please enter a city name."

    return render_template('index.html', weather=weather_data, error=error_message)

if __name__ == '__main__':
    # For production, use a more robust WSGI server like Gunicorn or uWSGI
    app.run(debug=True) # debug=True allows for automatic reloading on code changes