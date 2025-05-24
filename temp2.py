from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage
from langchain.schema.messages import ToolMessage
from langchain.tools import StructuredTool
from typing import Optional
import asyncio
import json


async def get_weather(location: str, unit: Optional[str] = "celsius") -> str:
    """Get the current weather for a location.

    Args:
        location: The city and state, e.g. San Francisco, CA or country e.g. France
        unit: The unit of temperature to return. Options are celsius or fahrenheit

    Returns:
        The current weather in the specified unit
    """
    return f"22C"


async def main():
    # Initialize the language model
    llm = ChatOpenAI(temperature=1, base_url="http://192.168.1.2:1234/v1", api_key="a", model="llama-xlam-2-8b-fc-r")

    # Define the tool
    weather_tool = StructuredTool.from_function(
        func=get_weather,
        name="get_weather",
        description="Get the current weather for a location"
    )

    # Create a dict of tools by name for easy lookup
    tools_map = {"get_weather": weather_tool}

    # Bind the tool to the language model
    llm_with_tools = llm.bind_tools([weather_tool])

    # Example query
    user_query = "What's the weather like in Tokyo?"

    # Initial message from user
    messages = [HumanMessage(content=user_query)]

    # Start conversation
    print("Starting conversation...")

    # Get initial LLM response
    response = await llm_with_tools.ainvoke(messages)
    print("LLM Response:", response)

    # Check for tool calls in additional_kwargs
    tool_calls = response.additional_kwargs.get('tool_calls', [])
    for tool_call in tool_calls:
        tool_name = tool_call.get('function', {}).get('name')
        print(f"Executing tool: {tool_name}")
        tool = tools_map[tool_name]

        # Parse arguments
        args_str = tool_call.get('function', {}).get('arguments', '{}')
        args = json.loads(args_str)
        print(f"Tool arguments: {args}")


        # Execute the tool
        tool_result = await tool.invoke()
        print(f"Tool result: {tool_result}")

        # Add the tool result to messages
        messages.append(AIMessage(content="", additional_kwargs={"tool_calls": [tool_call]}))
        messages.append(ToolMessage(content=str(tool_result), tool_call_id=tool_call.get('id')))

        # Get final response from LLM
        final_response = await llm.ainvoke(messages)
        print("Final LLM Response:", final_response.content)



if __name__ == "__main__":
    asyncio.run(main())
