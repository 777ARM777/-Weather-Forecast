import requests
from typing import Optional, Tuple, Dict, Any
from colorama import init, Fore, Style
from rich.console import Console
from rich.progress import track

init(autoreset=True)
cons = Console()

weather_cache = {}


def get_coordinates(api_key: str, city: Optional[str] = None, zip_code: Optional[str] = None, limit: int = 1) -> \
                    Optional[Tuple[float, float]]:
    """Get the latitude and longitude of a city using the OpenWeatherMap Geocoding API."""
    url = "https://api.openweathermap.org/geo/1.0/direct"
    params = {'q': f"{zip_code}" if zip_code else city, 'limit': limit, 'appid': api_key}
    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data:
            return data[0]['lat'], data[0]['lon']
        else:
            cons.print("[bold red]No info found for the given location.")
    else:
        cons.print(f"[bold red]Error: {response.status_code} - {response.json().get('message', 'Unknown error')}")
    return None


def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return (celsius * 9 / 5) + 32


def get_weather_data(lat: float, lon: float, api_key: str) -> Optional[Dict[str, Any]]:
    """Get current weather data for given coordinates."""
    global response
    key = (lat, lon)
    if key in weather_cache:
        return weather_cache[key]

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {'lat': lat, 'lon': lon, 'appid': api_key, 'units': 'metric'}

    for _ in track(range(10), description="Fetching weather data..."):
        response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        weather_cache[key] = data
        return data
    else:
        cons.print(f"[bold red]Error: {response.status_code} - {response.json().get('message', 'Unknown error')}")
    return None


def display_weather_info(weather_data: Dict[str, Any], temp_unit: int) -> None:
    """Display the weather information."""
    city = weather_data['name']
    country = weather_data['sys']['country']
    temp = weather_data['main']['temp']
    feels_like = weather_data['main']['feels_like']
    description = weather_data['weather'][0]['description'].capitalize()
    wind_speed = weather_data['wind']['speed']
    pressure = weather_data['main']['pressure']
    humidity = weather_data['main']['humidity']

    cons.print(f"{city}, {country}", style="red")
    if temp_unit == 2:
        temp_fahrenheit = celsius_to_fahrenheit(temp)
        feels_like_fahrenheit = celsius_to_fahrenheit(feels_like)
        cons.print(f"{temp_fahrenheit:.2f} °F", style="green")
        cons.print(f"Feels like {feels_like_fahrenheit:.2f} °F", style="green")
    else:
        cons.print(f"{temp:.2f} °C", style="green")
        cons.print(f"Feels like {feels_like:.2f} °C", style="green")

    cons.print(description, style="green")
    cons.print(f"Wind speed: {wind_speed} m/s", style="green")
    cons.print(f"Atmospheric pressure: {pressure} hPa", style="green")
    cons.print(f"Humidity: {humidity}%", style="green")


def get_temperature_unit() -> int:
    """Ask user for preferred temperature unit."""
    cons.print('1. Celsius\n2. Fahrenheit', style="white")
    while True:
        try:
            choice = int(input('Choose temperature unit Celsius or Fahrenheit. Please type 1 or 2: '))
            if choice in [1, 2]:
                return choice
            else:
                cons.print("[red]Invalid input. Please enter a number 1 or 2.")
        except ValueError:
            cons.print("[red]Invalid input. Please enter a number 1 or 2.")


if __name__ == '__main__':
    cons.print('Hi, it is a Simple Weather Forecast Application to help you get weather information quickly', style="bold white")

    api = '54977de5d5163840e6b2bee2f2b82731'

    city = input('Input the name of a city: ')
    if not city:
        zip_code = input('Input the ZIP code: ')
    else:
        zip_code = None

    coord = get_coordinates(api, city, zip_code)
    if coord:
        lat, lon = coord
        weather_data = get_weather_data(lat, lon, api)
        if weather_data:
            temp_unit = get_temperature_unit()
            display_weather_info(weather_data, temp_unit)
    else:
        cons.print("[red]Unable to get the coordinates for the given city.")
