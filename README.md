# City Intelligence Agent

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Click%20Here-success?style=for-the-badge)](https://your-demo-link.com) 

**City Intelligence Agent** is an AI-powered, interactive web application built with Streamlit and LangChain. It acts as a smart, conversational assistant capable of retrieving real-time data about any city in the world. By leveraging tool-calling capabilities, the agent autonomously decides when to fetch current weather, search for the latest news, or calculate driving routes based on natural language queries from the user.

## ✨ Key Features
* **Real-Time Weather Data:** Integrates with the Open-Meteo API to provide up-to-date temperature, humidity, and wind speed for any location, translated into plain language by the AI.
* **Latest News & City Exploration:** Uses the Tavily Search API to pull the most recent news, historical context, and tourist attraction information for specific cities.
* **Smart Routing & Navigation:** Connects to OpenRouteService to calculate driving distances and estimated travel durations between two locations.
* **Agentic Reasoning:** Powered by LangChain and Groq's high-speed inference (running the `llama-3.3-70b-versatile` model), the agent analyzes your prompt, picks the exact tools it needs, and synthesizes a comprehensive response.
* **Secure, Polished UI:** Features a custom "night map" themed Streamlit interface with chat bubbles, pulsing loading indicators, and secure, session-only API key inputs (keys are never saved to disk).

## 🛠️ Tech Stack
* **Frontend:** Streamlit (with custom CSS injection)
* **Orchestration:** LangChain (Agent & Tool creation)
* **LLM / Reasoning:** Groq API (`llama-3.3-70b-versatile`)
* **External APIs:**
  * Open-Meteo (Weather)
  * Nominatim / OpenStreetMap (Geocoding)
  * Tavily (Web Search & News)
  * OpenRouteService (Driving directions)

## ⚙️ How it Works
1. **User Input:** You ask a question like *"What's the weather like in Paris and how far is it to drive to Berlin?"*
2. **Tool Selection:** The LLM evaluates the prompt and determines it needs to call the `getweather` tool for Paris, and the `get_route` tool for Paris to Berlin.
3. **Execution:** The agent triggers those specific Python functions, fetching JSON data from the external APIs.
4. **Synthesis:** The LLM reads the returned raw data and formulates a conversational, easy-to-read response for the user in the UI.

## 🚀 Running Locally

1. Clone this repository
2. Install the required dependencies:
   ```bash
   pip install streamlit python-dotenv langchain-groq langchain-core tavily-python langchain requests
   ```
3. Run the application:
   ```bash
   streamlit run app.py
   ```
4. Enter your API keys (Groq, Tavily, OpenRouteService) directly in the sidebar securely to start using the agent.
