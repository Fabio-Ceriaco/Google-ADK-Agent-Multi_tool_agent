import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent


def get_geo_coordinates(city: str, country: str) -> dict:
    """Retrieves the geographical coordinates (latitude and longitude) for a specified city and country.

    Args:
        city (str): The name of the city to get the coordinates for.
        country (str): The name of the country where the city is located.

    Returns:
        dict: A dictionary containing the status and either the coordinates or an error message.
    """
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},{country}&limit=1&appid={settings.WEATHER_API_KEY}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data[0]["lat"], data[0]["lon"]

    else:
        return {
            "status": f"error: {response.status_code}",
            "error_message": f"Failed to retrieve geocoding data for {city}, {country}.",
        }


def get_weather_data(lat: float, lon: float) -> dict:
    """Retrieves the current weather data for the specified latitude and longitude.

    Args:
        lat (float): The latitude of the location to get the weather data for.
        lon (float): The longitude of the location to get the weather data for.

    Returns:
        dict: A dictionary containing the status and either the weather data or an error message.
    """
    url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=metric&appid={settings.WEATHER_API_KEY}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "temp": data["current"]["temp"],
            "main": data["current"]["weather"][0]["main"],
            "weather": data["current"]["weather"][0]["description"],
            "humidity": data["current"]["humidity"],
        }
    else:
        return {
            "status": f"error: {response.status_code}",
            "error_message": f"Failed to retrieve weather data for coordinates ({lat}, {lon}).",
        }


# Define the tools that the agent can use
def get_weather(city: str, country: str) -> dict:
    """Retrieves the current weather for a specified city.

    Args:
        city (str) : The name of the city to get the weather for.
        country (str) : The name of the country where the city is located.

    Returns:
        dict: status and results or error msg.

    """
    if not city or not country:
        return {
            "status": "error",
            "error_message": "City and country must be provided to get weather information.",
        }

    LAT, LON = get_geo_coordinates(city, country)
    if isinstance(LAT, dict) and LAT.get("status", "").startswith("error"):
        return LAT  # Return the error message from get_geo_coordinates
    weather_data = get_weather_data(LAT, LON)
    if isinstance(weather_data, dict) and weather_data.get("status", "").startswith(
        "error"
    ):
        return weather_data  # Return the error message from get_weather_data
    temp = weather_data["temp"]
    main = weather_data["main"]
    weather = weather_data["weather"]
    humidity = weather_data["humidity"]

    if temp and main and weather and humidity:
        return {
            "status": "success",
            "report": (
                f"The weather in {city} is currently {main} with a temperature of {temp}"
                f" degrees Celsius ({temp * 9/5 +32} degrees Fahrenheit) and humidity of {humidity}%."
            )
        }
    else:
        return {
                "status": "error",
                "error_message": f"Failed to retrieve complete weather data for {city}.",
            }
    




root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=("Agent to answer questions about the time and weather in a city."),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[get_weather, get_geo_coordinates, get_weather_data],
)
