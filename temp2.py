from datetime import datetime, timezone

import aiohttp
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.schema.messages import ToolMessage
from langchain.tools import StructuredTool
from typing import Optional, List, Dict, Any
import asyncio
import json


async def find_hotels(city_name: str, check_in_date_iso: str, check_out_date_iso: str, adults_count: int,
                      children_count: int) -> str:

   async with aiohttp.request("GET", "http://192.168.1.2:8000/search-city", params={"city": city_name}) as response:
       response_json = await response.json()

   city_id = response_json["cityId"]
   city_name = response_json["cityName"]

   async with aiohttp.request("GET", "http://192.168.1.2:8000/find-hotels-of-city", params={"cityId": city_id, "cityName": city_name,
                                                                                       "checkInDate": check_in_date_iso,
                                                                                       "checkOutDate": check_out_date_iso,
                                                                                       "adultsCount": adults_count,
                                                                                       "childrenCount": children_count}) as response:
        return await response.text()


async def get_current_datetime():
    return datetime.now().astimezone().replace(microsecond=0).isoformat()



async def chat_loop():
    # Initialize the language model
    llm = ChatOpenAI(temperature=0.1, base_url="http://192.168.1.2:1234/v1", api_key="a", model="hermes-2-pro-mistral-7b")

    # Create a dict of tools by name for easy lookup
    tools = [StructuredTool.from_function(
        func=find_hotels,
        name="find_hotels",
        description="Find hotels in a city for given dates and number of guests"
    ),
    StructuredTool.from_function(
            func=get_current_datetime,
            name="get_current_datetime",
            description="Get current local datetime"
        ),
    ]
    tools_map = {tool.name: tool for tool in tools}

    # Bind the tools to the language model
    llm_with_tools = llm.bind_tools(tools)

    # Initialize conversation history
    messages = []

    print("Chat started. Type 'exit' to end the conversation.")

    while True:
        # Get user input
        user_input = input("You: ")

        if user_input.lower() == 'exit':
            print("Chat ended.")
            break

        # Add user message to history
        messages.append(HumanMessage(content=user_input))

        # Process with LLM and handle tool calls until we get a final response
        while True:
            # Get LLM response
            llm_response = await llm_with_tools.ainvoke(messages)

            # Check for tool calls
            tool_calls = llm_response.additional_kwargs.get('tool_calls', [])

            # If no tool calls, we have our final response
            if not tool_calls:
                print(f"AI: {llm_response.content}")
                messages.append(llm_response)
                break

            # Process each tool call
            messages.append(llm_response)

            for tool_call in tool_calls:
                tool_name = tool_call.get('function', {}).get('name')
                print(f"[System] Executing tool: {tool_name}")

                if tool_name in tools_map:
                    tool = tools_map[tool_name]

                    # Parse arguments
                    args_str = tool_call.get('function', {}).get('arguments', '{}')
                    args = json.loads(args_str)

                    # Execute the tool
                    tool_result = await tool.invoke(args)

                    # For better readability in console
                    if isinstance(tool_result, list) and len(tool_result) > 0:
                        print(f"[System] Tool returned {len(tool_result)} results")
                    else:
                        print(f"[System] Tool result: {tool_result}")

                    # Add tool result to message history
                    tool_message = ToolMessage(
                        content=json.dumps(tool_result) if isinstance(tool_result, (dict, list)) else str(tool_result),
                        tool_call_id=tool_call.get('id')
                    )
                    messages.append(tool_message)
                else:
                    print(f"[System] Unknown tool: {tool_name}")
                    # Add error message as tool result
                    tool_message = ToolMessage(
                        content=f"Error: Tool '{tool_name}' not found",
                        tool_call_id=tool_call.get('id')
                    )
                    messages.append(tool_message)


async def main():
    await chat_loop()


if __name__ == "__main__":
    asyncio.run(main())
