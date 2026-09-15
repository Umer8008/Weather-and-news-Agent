import os
import requests
from langchain.agents import create_agent
from dotenv import load_dotenv
from rich import print
from tavily import TavilyClient
from langchain_mistralai import ChatMistralAI
from langchain.tools import tool
from langchain_core.messages import (
    HumanMessage,
    ToolMessage,
)
from langchain.agents.middleware import wrap_tool_call

# ============================================================
# ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# WEATHER TOOL
# ============================================================

@tool
def get_weather(city: str) -> str:
    """
    Get the current weather for a given city.
    """

    api_key = os.getenv("OPENWEATHER_API_KEY")

    if not api_key:
        return "Error: OPENWEATHER_API_KEY was not found in .env"

    url = "https://api.openweathermap.org/data/2.5/weather"

    params = {
        "q": city,
        "appid": api_key,
        "units": "metric",
    }

    try:
        response = requests.get(
            url,
            params=params,
            timeout=10
        )

        if response.status_code != 200:
            return (
                f"Error {response.status_code}: "
                f"{response.text}"
            )

        data = response.json()

        temperature = data["main"]["temp"]
        description = data["weather"][0]["description"]

        return (
            f"The current weather in {city} is "
            f"{temperature}°C with {description}."
        )

    except requests.RequestException as e:
        return f"Weather API request failed: {e}"

    except KeyError:
        return "Error: Unexpected response received from weather API."


# ============================================================
# TEST WEATHER TOOL
# ============================================================

#print("\nTesting Weather Tool")

#weather_result = get_weather.invoke(
#    {"city": "Rawalpindi"}
#)

#print(weather_result)


# ============================================================
# TAVILY NEWS TOOL
# ============================================================

@tool
def get_latest_news(city: str) -> str:
    """
    Get the latest news about a given city using Tavily.
    """

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        return "Error: TAVILY_API_KEY was not found in .env"

    try:
        tavily_client = TavilyClient(
            api_key=api_key
        )

        query = f"latest news in {city}"

        response = tavily_client.search(
            query=query,
            topic="news",
            search_depth="advanced",
            max_results=5,
        )

        results = response.get("results", [])

        if not results:
            return f"No recent news found for {city}."

        news = []

        for index, result in enumerate(results, start=1):

            title = result.get(
                "title",
                "No title"
            )

            content = result.get(
                "content",
                "No description available"
            )

            url = result.get(
                "url",
                "No URL available"
            )

            news.append(
                f"{index}. {title}\n"
                f"   {content}\n"
                f"   Source: {url}"
            )

        return "\n\n".join(news)

    except Exception as e:
        return f"Tavily request failed: {e}"


# ============================================================
# TEST NEWS TOOL
# ============================================================

#print("\nTesting News Tool")

#news_result = get_latest_news.invoke(
#    {"city": "Rawalpindi"}
#)

#print(news_result)
#========================================================================
# Wrap the tools with the middleware to ensure they are called correctly
#========================================================================

@wrap_tool_call
def human_approval(request, handler):
    tool_name = request.tool_call["name"]
    tool_args = request.tool_call["args"]

    print(f"\nThe agent wants to call: {tool_name}")
    print(f"Arguments: {tool_args}")

    approval = input("Allow this tool call? (yes/no): ")

    if approval.lower() in ["y", "yes"]:
        return handler(request)

    return ToolMessage(
        content="The user rejected this tool call.",
        tool_call_id=request.tool_call["id"],
    )
# ============================================================
# LLM
# ============================================================


llm = ChatMistralAI(
    model="mistral-small-latest",
    api_key=os.getenv("MISTRAL_API_KEY"),
)

agent = create_agent(
    model=llm,
    tools=[get_weather, get_latest_news],
    middleware=[human_approval],
    system_prompt="You are a helpful assistant that provides weather updates and the latest news about cities."
)

print("\n" + "=" * 60)
print("Umer's City Intelligence System")
print("Type 'exit' to quit the program.")
print("=" * 60)

while True:

    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        print("Exiting the program. Goodbye!")
        break

    result = agent.invoke({
        "messages": [
            {"role": "user", "content": user_input}
        ]
    })

    print(f"\nAgent: {result['messages'][-1].content}")