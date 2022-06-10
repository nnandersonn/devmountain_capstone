import requests
import os
from dotenv import load_dotenv

load_dotenv()
WEATHER_API = os.getenv('WEATHER_API')



def get_forecast(city):

    parameters = {
        "q": city,
        "days": 1
    }

    response = requests.get(url=f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API}", params = parameters )
    current_weather = response.json()['current']['condition']['text']
    current_weather_icon = response.json()['current']['condition']['icon']
    current_temp = round(response.json()['current']['temp_f'])
    weather = {"current_weather": current_weather, "current_weather_icon": current_weather_icon, "current_temp": current_temp}

    return (weather)


