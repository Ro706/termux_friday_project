import datetime
import requests
from backend.TextToSpeech import speak
import geocoder

# Get user's location based on IP address
g = geocoder.ip('me')

class Weather:
    def __init__(self, city):
        """Initialize Weather class with city name"""
        self.city = city
        
    def get_weather(self):
        """Get weather data for the city"""
        api_key = '04018081b69cca6f721c5ed1a46be071'
        base_url = 'https://api.openweathermap.org/data/2.5/weather?'
        url = f"{base_url}appid={api_key}&q={self.city}&units=metric"
        
        response = requests.get(url)
        data = response.json()
        
        if data['cod'] != 401:
            # Extract weather information
            city_name = data['name']
            weather_condition = data['weather'][0]['main']
            temperature = data['main']['temp']
            temp_min = data['main']['temp_min']
            temp_max = data['main']['temp_max']
            
            # Return data for use in wish_me function
            return {
                'city_name': city_name,
                'weather_condition': weather_condition,
                'temperature': temperature
            }
        else:
            print('City not found or API error')
            speak('City not found or API error')
            return None
        
def tell_me_todays_weather():
    """Function to get and speak current weather at user's location"""
    city_name = g.city
    weather_obj = Weather(city_name)
    return weather_obj.get_weather()

def wish_me(name):
    """Greet user based on time of day and current weather"""
    # Get weather data
    weather_data = tell_me_todays_weather()
    
    if not weather_data:
        return f"Hello {name}, I couldn't retrieve the weather information right now."
    
    temperature = weather_data['temperature']
    weather_condition = weather_data['weather_condition']
    
    # Get current hour
    hour = datetime.datetime.now().hour
    
    # Create appropriate greeting based on time of day
    if hour < 12:
        greeting = f"Good morning, {name}! ☀️ Hope you have a fantastic day ahead! The current temperature is {temperature}°C, with {weather_condition}. A perfect time to step out for a fresh start!"
    elif 12 <= hour < 18:
        greeting = f"Hey {name}! 🌞 It's a bright and sunny afternoon with {temperature}°C outside. Stay hydrated and don't forget your sunglasses!"
    elif 18 <= hour < 21:
        greeting = f"Good evening, {name}! 🌆 The temperature is now {temperature}°C, with {weather_condition}. A great time for a walk or some relaxation!"
    else:
        greeting = f"Hello {name}, it's nighttime now! 🌃 The temperature is {temperature}°C with {weather_condition}. Have a restful night!"
    
    print(greeting)
    speak(greeting)
    return greeting

# Main execution
if __name__ == "__main__":
    user_name = input("What's your name? ")
    wish_me(user_name)