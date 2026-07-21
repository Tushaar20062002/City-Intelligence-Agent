import os
import requests
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from tavily import TavilyClient
from langchain.agents import create_agent

load_dotenv()

SYSTEM_PROMPT = """
You are a City Intelligence Assistant.

Responsibilities:
- Use the weather tool for weather queries, and add your own plain-language
  explanation (e.g. heavy rain, heat, cold) alongside the numbers.
- Use the news tool for news queries.
- Use the search tool for general city information.
- Use Route tool for getting routes for the users.
- If multiple tools are required, call all necessary tools before answering.
"""

def build_tools(tavily_key: str, ors_key: str):
    @tool
    def getweather(city: str) -> dict:
        """Get current weather of the city."""
        geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}&count=1"
        geo = requests.get(geo_url, timeout=15).json()
        if "results" not in geo:
            return {"error": "City not found."}

        lat = geo["results"][0]["latitude"]
        lon = geo["results"][0]["longitude"]

        weather_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={lat}&longitude={lon}"
            "&current=temperature_2m,relative_humidity_2m,wind_speed_10m"
        )
        weather = requests.get(weather_url, timeout=15).json()
        return weather.get("current", {"error": "No current weather available."})

    @tool
    def latest_news(city: str):
        """
        Search for tourist attractions, famous places, city history, culture,
        restaurants, hotels, monuments, parks, museums, and landmarks.
        """
        if not tavily_key:
            return {"error": "Tavily API key not configured."}
        client = TavilyClient(api_key=tavily_key)
        response = client.search(query=f"Latest news about {city}", search_depth="advanced", max_results=5)
        return [
            {"title": item["title"], "url": item["url"], "summary": item["content"]}
            for item in response["results"]
        ]

    def get_coordinates(place):
        url = "https://nominatim.openstreetmap.org/search"
        params = {"q": place, "format": "json", "limit": 1}
        headers = {"User-Agent": "City-Agent"}
        response = requests.get(url, params=params, headers=headers, timeout=15)
        data = response.json()
        if not data:
            return None
        return float(data[0]["lat"]), float(data[0]["lon"])

    @tool
    def get_route(start: str, destination: str):
        """Get driving directions between two locations.

        Use ONLY for directions, navigation, route, distance, or travel between
        two places. Do NOT use for tourist places, history, hotels, or restaurants.
        """
        if not ors_key:
            return {"error": "OpenRouteService API key not configured."}

        start_coord = get_coordinates(start)
        end_coord = get_coordinates(destination)
        if not start_coord or not end_coord:
            return {"error": "Location not found."}

        headers = {"Authorization": ors_key, "Content-Type": "application/json"}
        body = {"coordinates": [[start_coord[1], start_coord[0]], [end_coord[1], end_coord[0]]]}
        response = requests.post(
            "https://api.openrouteservice.org/v2/directions/driving-car",
            headers=headers, json=body, timeout=20,
        )
        data = response.json()
        if "routes" not in data:
            return {"error": data.get("error", "Route not found.")}
        summary = data["routes"][0]["summary"]
        return {
            "distance_km": round(summary["distance"] / 1000, 2),
            "duration_min": round(summary["duration"] / 60, 2),
        }

    return [getweather, get_route, latest_news]


def build_agent(groq_key: str, tavily_key: str, ors_key: str):
    llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0, api_key=groq_key)
    tools = build_tools(tavily_key, ors_key)
    return create_agent(model=llm, tools=tools, system_prompt=SYSTEM_PROMPT)
