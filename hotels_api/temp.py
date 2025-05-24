import json
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional


# Simulated weather function
async def get_weather(location: str, unit: str = "celsius") -> str:
    """Get weather information for a location."""

    print("CALLING WEATCHER FOR", location)
    await asyncio.sleep(0.5)  # Simulate API call
    temp_symbol = "°C" if unit == "celsius" else "°F"
    return f"Current weather in {location} is 22{temp_symbol}, sunny with light clouds."


async def call_xlam_api(session: aiohttp.ClientSession, api_url: str, request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Make an async API call to the xLAM model."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer a"  # This is a placeholder
    }

    async with session.post(api_url, headers=headers, json=request_data) as response:
        response.raise_for_status()
        return await response.json()


async def main():
    # API endpoint
    api_url = "http://192.168.1.2:1234/v1/chat/completions"

    # Define the weather function for the model
    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_weather",
                "description": "Get the current weather for a location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city name, e.g. London"
                        },
                        "unit": {
                            "type": "string",
                            "enum": ["celsius", "fahrenheit"],
                            "description": "The unit of temperature to return"
                        }
                    },
                    "required": ["location"]
                }
            }
        }
    ]

    # Initial conversation
    messages = [
        {"role": "user", "content": "How you doin?"}
    ]

    try:
        async with aiohttp.ClientSession() as session:
            # Step 1: Ask about London weather
            print("Step 1: Asking about London weather...")
            request_data = {
                "model": "llama-xlam-2-8b-fc-r",
                "messages": messages,
                "tools": tools,
                "temperature": 0
            }

            # Make the API call asynchronously
            response_data = await call_xlam_api(session, api_url, request_data)

            # Extract the assistant's message
            assistant_message = response_data["choices"][0]["message"]
            print(f"\nAssistant: {json.dumps(assistant_message, indent=2)}")

            # Check if the model wants to call a function
            if "tool_calls" in assistant_message:
                tool_call = assistant_message["tool_calls"][0]
                function_name = tool_call["function"]["name"]
                function_args = json.loads(tool_call["function"]["arguments"])

                print(f"\nFunction call: {function_name}")
                print(f"Arguments: {json.dumps(function_args, indent=2)}")

                # Execute the function asynchronously
                location = function_args.get("location")
                unit = function_args.get("unit", "celsius")
                result = await get_weather(location, unit)
                print(f"Function result: {result}")

                # Step 2: Send the function result back to the model
                print("\nStep 2: Sending function result back to the model...")
                messages.append(assistant_message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": function_name,
                    "content": result
                })

                # Make another API call with the updated messages
                request_data = {
                    "model": "llama-xlam-2-8b-fc-r",
                    "messages": messages,
                    "tools": tools,
                    "temperature": 0
                }

                response_data = await call_xlam_api(session, api_url, request_data)

                # Extract the assistant's response
                final_message = response_data["choices"][0]["message"]
                print(f"\nFinal response: {final_message['content']}")

                # Step 3: Ask about Tokyo weather in fahrenheit
                print("\nStep 3: Asking about Tokyo weather in fahrenheit...")
                messages.append(final_message)
                messages.append({"role": "user", "content": "What about the weather in Tokyo in fahrenheit?"})

                # Make another API call for Tokyo asynchronously
                request_data = {
                    "model": "llama-xlam-2-8b-fc-r",
                    "messages": messages,
                    "tools": tools,
                    "temperature": 0
                }

                response_data = await call_xlam_api(session, api_url, request_data)

                # Extract the assistant's message for Tokyo
                tokyo_message = response_data["choices"][0]["message"]
                print(f"\nTokyo query response: {json.dumps(tokyo_message, indent=2)}")

                # Check if the model wants to call a function for Tokyo
                if "tool_calls" in tokyo_message:
                    tokyo_call = tokyo_message["tool_calls"][0]
                    tokyo_args = json.loads(tokyo_call["function"]["arguments"])

                    # Execute the function for Tokyo asynchronously
                    tokyo_location = tokyo_args.get("location")
                    tokyo_unit = tokyo_args.get("unit", "fahrenheit")
                    tokyo_result = await get_weather(tokyo_location, tokyo_unit)
                    print(f"Function result for Tokyo: {tokyo_result}")

                    # Step 4: Send the Tokyo function result back
                    print("\nStep 4: Sending Tokyo function result back...")
                    messages.append(tokyo_message)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tokyo_call["id"],
                        "name": tokyo_call["function"]["name"],
                        "content": tokyo_result
                    })

                    # Final API call asynchronously
                    request_data = {
                        "model": "llama-xlam-2-8b-fc-r",
                        "messages": messages,
                        "tools": tools,
                        "temperature": 0
                    }

                    response_data = await call_xlam_api(session, api_url, request_data)

                    # Extract the final response
                    final_tokyo_message = response_data["choices"][0]["message"]
                    print(f"\nFinal Tokyo response: {final_tokyo_message['content']}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main()) 