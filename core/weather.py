import requests
from backend.TextToSpeech import speak
import geocoder

class weather:
    def __init__(self,city) :
        self.city = city
    def weather(self):
        api_key ='04018081b69cca6f721c5ed1a46be071'
        base_url = 'https://api.openweathermap.org/data/2.5/weather?'
        url = base_url+'appid='+api_key+'&q='+self.city+'&units=metric'
        response = requests.get(url)
        x=response.json()
        if x['cod']!=401:
            city_name = x['name']
            weather_desc = x['weather'][0]['main']
            temp = x['main']['temp']
            temp_min = x['main']['temp_min']
            temp_max = x['main']['temp_max']
            
            report = f"Weather in {city_name}: {weather_desc}, Temperature: {temp}°C, Min: {temp_min}°C, Max: {temp_max}°C"
            speak(report)
            return report
        else:
            return "City not found"

def tellmeTodaysWeather():
    g = geocoder.ip('me')
    name = g.city
    obj = weather(name)
    return obj.weather()

if __name__ == "__main__":
    print(tellmeTodaysWeather())
