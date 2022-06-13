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

def should_i_walk(temp, condition):
    
    if temp < 32:
        return "It is freezing out there! Bundle up."
    elif temp < 64 and 'rain' in condition:
        return "It's cold and rainy out. Don't forget that umbrella."
    elif temp < 64:
        return "It's cold out but no rain in sight!"
    elif temp < 76 and 'rain' in condition:
        return "It's a comfortable temperature but raining."
    elif temp <76:
        return "You couldn't ask for better weather! Get out there with your pack and enjoy!"
    elif temp < 90:
        return "It's a warm one out there! Brind water for you and your pack."
    elif temp >= 90:
        return "It's pretty hot out there. Are you sure you want to leave the house?"
        