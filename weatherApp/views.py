import datetime
import requests
from django.shortcuts import render
from django.core.cache import cache


def home(request):
    """Render home.html template"""

    # Get API key from openweathermap.org
    API_KEY = open("API_KEY", "r").read().strip()
    current_weather_url = "https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid={}"
    forecast_weather_url = "https://api.openweathermap.org/data/2.5/onecall?lat={}&lon={}&units=metric&appid={}&exclude=current,minutely,hourly,alerts"

    if request.method == 'POST':
        city1 = request.POST['city1']
        city2 = request.POST.get('city2', None)

        weather_data1, daily_forecast1 = fetch_weather_and_forecast(city1, API_KEY, current_weather_url, forecast_weather_url)
        bg_color1 = change_background_color(city1, API_KEY, current_weather_url)
        if city2:
            weather_data2, daily_forecast2 = fetch_weather_and_forecast(city2, API_KEY, current_weather_url, forecast_weather_url)
            bg_color2 = change_background_color(city2, API_KEY, current_weather_url)
        else:
            weather_data2, daily_forecast2, bg_color2 = None, None, None

        
        context = {
            'weather_data1': weather_data1,
            'daily_forecast1': daily_forecast1,
            'weather_data2': weather_data2,
            'daily_forecast2': daily_forecast2,
            'bg_color1': bg_color1,
            'bg_color2': bg_color2,
        }
        return render(request, 'weatherApp/home.html', context)
    else:
        return render(request, 'weatherApp/home.html')
    

def fetch_weather_and_forecast(city, api_key, current_weather_url, forecast_weather_url):
    # Try to get data from cache first
    weather_data = cache.get(f'{city}_weather_data')
    daily_forecast = cache.get(f'{city}_daily_forecast')

    # If data is not in cache, make API calls and store results in cache
    if not weather_data or not daily_forecast:
        current_weather_response = requests.get(current_weather_url.format(city, api_key))
        current_weather_response.raise_for_status()
        current_weather = current_weather_response.json()

        forecast_response = requests.get(forecast_weather_url.format(current_weather['coord']['lat'], current_weather['coord']['lon'], api_key))
        forecast_response.raise_for_status()
        forecast_weather = forecast_response.json()

        weather_data = {
            'city': city,
            'temperature': round(current_weather['main']['temp'], 2),
            'description': current_weather['weather'][0]['description'],
            'icon': current_weather['weather'][0]['icon'],
            'humidity': current_weather['main']['humidity'],
            'wind_speed': current_weather['wind']['speed'],
            'pressure': current_weather['main']['pressure'],
            'sunrise': datetime.datetime.fromtimestamp(current_weather['sys']['sunrise']).strftime('%H:%M:%S'),
            'sunset': datetime.datetime.fromtimestamp(current_weather['sys']['sunset']).strftime('%H:%M:%S'),
        }

        daily_forecast = []
        for data in forecast_weather['daily'][:5]:
            daily_forecast.append({
                'date': datetime.datetime.fromtimestamp(data['dt']).strftime('%d-%m-%Y'),
                'temperature': round(data['temp']['day'], 2),
                'description': data['weather'][0]['description'],
                'icon': data['weather'][0]['icon'],
                'humidity': data['humidity'],
                'wind_speed': data['wind_speed'],
                'pressure': data['pressure'],
            })

        # Store results in cache for 10 minutes (600 seconds)
        cache.set(f'{city}_weather_data', weather_data, 600)
        cache.set(f'{city}_daily_forecast', daily_forecast, 600)

    return weather_data, daily_forecast


def change_background_color(city, api_key, current_weather_url):


    current_weather_response = requests.get(current_weather_url.format(city, api_key))
    current_weather_response.raise_for_status()
    current_weather = current_weather_response.json()
    description = current_weather['weather'][0]['description']

    if description == 'clear sky':
        bg_color = 'blue'
    elif description == 'few clouds':
        bg_color = 'lightblue'
    elif description == 'scattered clouds':
        bg_color = 'lightgrey'
    elif description == 'broken clouds':
        bg_color = 'grey'
    elif description == 'shower rain':
        bg_color = 'lightseagreen'
    elif description == 'rain':
        bg_color = 'darkblue'
    elif description == 'thunderstorm':
        bg_color = 'darkgrey'
    elif description == 'snow':
        bg_color = 'white'
    elif description == 'mist':
        bg_color = 'lemonchiffon'
    else:
        bg_color = 'lightgreen'
    
    return bg_color