from langchain_core.tools import tool
from langchain.agents import create_openai_functions_agent
from langchain.agents import AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
import asyncio
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import random

# Load environment variables
load_dotenv()

# Configure the model - using LM Studio's OpenAI-compatible endpoint
model = ChatOpenAI(
    model="your_chosen_model",  # Replace with the model you load in LM Studio
    base_url="http://192.168.1.2:1234/v1",  # Default LM Studio API URL
    api_key="lm-studio",  # LM Studio default API key
    temperature=0.1
)

# Mock hotel database
MOCK_HOTELS = {
    "new york": [
        {
            "id": "ny001",
            "name": "Grand Central Hotel",
            "address": "123 Park Avenue, New York",
            "stars": 4.5,
            "price_per_night": 299,
            "amenities": ["Free WiFi", "Pool", "Fitness Center", "Restaurant"],
            "available": True
        },
        {
            "id": "ny002",
            "name": "Manhattan Skyline Hotel",
            "address": "456 Broadway, New York",
            "stars": 5,
            "price_per_night": 450,
            "amenities": ["Free WiFi", "Spa", "Fitness Center", "Multiple Restaurants", "Bar"],
            "available": True
        },
        {
            "id": "ny003",
            "name": "Downtown Budget Inn",
            "address": "789 Canal Street, New York",
            "stars": 3,
            "price_per_night": 150,
            "amenities": ["Free WiFi", "Continental Breakfast"],
            "available": True
        }
    ],
    "paris": [
        {
            "id": "pr001",
            "name": "Seine River Hotel",
            "address": "123 Rue de Rivoli, Paris",
            "stars": 4,
            "price_per_night": 280,
            "amenities": ["Free WiFi", "Restaurant", "Bar", "Room Service"],
            "available": True
        },
        {
            "id": "pr002",
            "name": "Eiffel View Suites",
            "address": "456 Avenue Montaigne, Paris",
            "stars": 5,
            "price_per_night": 520,
            "amenities": ["Free WiFi", "Spa", "Fitness Center", "Michelin Star Restaurant", "Concierge"],
            "available": True
        }
    ],
    "london": [
        {
            "id": "ln001",
            "name": "Westminster Palace Hotel",
            "address": "123 Baker Street, London",
            "stars": 4.5,
            "price_per_night": 310,
            "amenities": ["Free WiFi", "Restaurant", "Fitness Center", "Tea Service"],
            "available": True
        },
        {
            "id": "ln002",
            "name": "Piccadilly Inn",
            "address": "456 Oxford Street, London",
            "stars": 3.5,
            "price_per_night": 210,
            "amenities": ["Free WiFi", "Breakfast Included", "Bar"],
            "available": True
        }
    ],
    "tokyo": [
        {
            "id": "tk001",
            "name": "Shinjuku Sky Hotel",
            "address": "123 Shinjuku, Tokyo",
            "stars": 4,
            "price_per_night": 275,
            "amenities": ["Free WiFi", "Restaurant", "Public Bath", "Convenience Store"],
            "available": True
        },
        {
            "id": "tk002",
            "name": "Imperial Gardens Resort",
            "address": "456 Chiyoda, Tokyo",
            "stars": 5,
            "price_per_night": 480,
            "amenities": ["Free WiFi", "Multiple Restaurants", "Spa", "Fitness Center"],
            "available": True
        }
    ]
}


# Async Hotel API tool with mock data
@tool
async def search_hotels(city: str, check_in_date: str) -> List[Dict]:
    """
    Search for available hotels in a specified city and check-in date.

    Args:
        city: The city to search for hotels (e.g., "New York", "Paris")
        check_in_date: The check-in date in YYYY-MM-DD format

    Returns:
        A list of available hotels with details
    """
    # Simulate network delay
    await asyncio.sleep(1)

    city_lower = city.lower()

    # Check if we have data for this city
    if city_lower in MOCK_HOTELS:
        # Add random availability based on date (just for simulation)
        hotels = MOCK_HOTELS[city_lower].copy()

        # Simulate some hotels being unavailable on certain dates
        for hotel in hotels:
            # Use check_in_date to seed random generator for consistent results
            date_seed = sum(ord(c) for c in check_in_date)
            random.seed(hotel["id"] + str(date_seed))
            hotel["available"] = random.random() > 0.3  # 30% chance of being unavailable

        # Filter to only available hotels
        available_hotels = [hotel for hotel in hotels if hotel["available"]]

        return {
            "city": city,
            "check_in_date": check_in_date,
            "available_hotels": available_hotels,
            "total_results": len(available_hotels)
        }
    else:
        return {
            "city": city,
            "check_in_date": check_in_date,
            "available_hotels": [],
            "total_results": 0,
            "message": f"No hotels found in {city}. Try another city like New York, Paris, London, or Tokyo."
        }


# Create prompt template
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful hotel search assistant. Your job is to help users find available hotels 
    in their desired location and dates. Ask for any missing information you need to perform the search.
    When showing hotel results, format them in a clear, readable way with important details like price, 
    star rating, and amenities. Currently, you can search for hotels in New York, Paris, London, and Tokyo."""),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create the agent
agent = create_openai_functions_agent(model, [search_hotels], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[search_hotels], verbose=True)


# Async chat function
async def process_message(user_input, chat_history):
    response = await agent_executor.ainvoke({
        "input": user_input,
        "chat_history": chat_history
    })
    return response["output"]


# Interactive chat loop
async def chat():
    chat_history = []
    print("Hotel Search Assistant (type 'quit' to exit)")
    print("------------------------------------------")
    print("You can search for hotels in: New York, Paris, London, Tokyo")

    while True:
        user_input = input("> ")
        if user_input.lower() == 'quit':
            break

        # Process the user input asynchronously
        response = await process_message(user_input, chat_history)

        # Display the response
        print(response)

        # Update chat history
        chat_history.append(("human", user_input))
        chat_history.append(("ai", response))



# Run the chat loop if executed directly
if __name__ == "__main__":
    asyncio.run(chat())