from datetime import datetime
from typing import Dict

import requests

from .plugin import Plugin


class WeatherPlugin(Plugin):
    """
    A plugin to get the current weather and 7-day daily forecast for a location
    """

    def get_source_name(self) -> str:
        return "OpenMeteo"

    def get_spec(self) -> [Dict]:
        latitude_param = {"type": "string", "description": "Latitude of the location"}
        longitude_param = {"type": "string", "description": "Longitude of the location"}
        unit_param = {
            "type": "string",
            "enum": ["celsius", "fahrenheit"],
            "description": "The temperature unit to use. Infer this from the provided location.",
        }
        daily_param = {
            "type": "string",
            "description": "what needs",
        }
        return [
            {
                "name": "get_current_weather",
                "description": "Get the current weather for a location using Open Meteo APIs.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": latitude_param,
                        "longitude": longitude_param,
                        "unit": unit_param,
                    },
                    "required": ["latitude", "longitude", "unit"],
                },
            },
            {
                "name": "get_forecast_weather",
                "description": "Get daily weather forecast for a location using Open Meteo APIs."
                               f"Today is {datetime.today().strftime('%A, %B %d, %Y')}",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "latitude": latitude_param,
                        "longitude": longitude_param,
                        "unit": unit_param,
                        "forecast_days": {
                            "type": "integer",
                            "description": "The number of days to forecast, including today. Default is 7. Max 14. "
                                           "Use 1 for today, 2 for today and tomorrow, and so on.",
                        },
                        "daily": daily_param,
                    },
                    "required": ["latitude", "longitude", "unit", "forecast_days"],
                },
            }
        ]
        
    #"weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_mean,rain_sum,precipitation_hours,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant"

    async def execute(self, function_name, helper, **kwargs) -> Dict:
        url = f'https://api.open-meteo.com/v1/forecast' \
              f'?latitude={kwargs["latitude"]}' \
              f'&longitude={kwargs["longitude"]}' \
              f'&temperature_unit={kwargs["unit"]}'
        if function_name == 'get_current_weather':
            #url += '&current_weather=true'
            url += '&hourly=temperature_2m,freezing_level_height,precipitation_probability,wind_speed_180m,wind_direction_180m,visibility'
            url += f'&wind_speed_unit={"ms"}'
            
            response = requests.get(url).json()
            results = {}
            print(response)
            for i, time in enumerate(response["hourly"]["time"]):
                results[datetime.strptime(time, "%Y-%m-%dT%H:%M").strftime("%A, %B %d, %Y %H:%M")] = {
                    "temperature_2m": response["hourly"]["temperature_2m"][i],
                    "freezing_level_height": response["hourly"]["freezing_level_height"][i],
                    #"dew_point_2m": response["hourly"]["dew_point_2m"][i],
                    "precipitation_probability": response["hourly"]["precipitation_probability"][i],
                    #"rain": response["hourly"]["rain"][i],
                    #"wind_direction_10m": response["hourly"]["wind_direction_10m"][i],
                    "wind_direction_180m": response["hourly"]["wind_direction_180m"][i],
                    #"wind_speed_10m": response["hourly"]["wind_speed_10m"][i],
                    "wind_speed_180m": response["hourly"]["wind_speed_180m"][i],
                    "visibility": response["hourly"]["visibility"][i],
                    #"snow_depth": response["hourly"]["snow_depth"][i],
                }
            return {"today": datetime.today().strftime("%A, %B %d, %Y"), "forecast": results}
            #return requests.get(url).json()

        elif function_name == 'get_forecast_weather':
            url += '&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_mean,rain_sum,precipitation_hours,wind_speed_10m_max,wind_gusts_10m_max,wind_direction_10m_dominant,'
            url += f'&forecast_days={kwargs["forecast_days"]}'
            url += f'&wind_speed_unit={"ms"}'
            url += '&timezone=auto'
            response = requests.get(url).json()
            results = {}
            for i, time in enumerate(response["daily"]["time"]):
                results[datetime.strptime(time, "%Y-%m-%d").strftime("%A, %B %d, %Y")] = {
                    "weathercode": response["daily"]["weathercode"][i],
                    "temperature_2m_max": response["daily"]["temperature_2m_max"][i],
                    "temperature_2m_min": response["daily"]["temperature_2m_min"][i],
                    "precipitation_probability_mean": response["daily"]["precipitation_probability_mean"][i],
                    "rain_sum": response["daily"]["rain_sum"][i],
                    "precipitation_hours": response["daily"]["precipitation_hours"][i],
                    "wind_speed_10m_max": response["daily"]["wind_speed_10m_max"][i],
                    "wind_gusts_10m_max": response["daily"]["wind_gusts_10m_max"][i],
                    "wind_direction_10m_dominant": response["daily"]["wind_direction_10m_dominant"][i],
                }
            return {"today": datetime.today().strftime("%A, %B %d, %Y"), "forecast": results}
