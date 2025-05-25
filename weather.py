from datetime import datetime, timezone
import aiohttp
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.schema.messages import ToolMessage
from langchain.tools import StructuredTool
from typing import Optional, List, Dict, Any
import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

async def find_hotel_comments(hotel_id: int) -> str:
    async with aiohttp.request("GET", "http://192.168.1.2:8000/get-comments-by-hotel", params={"hotelId": hotel_id}) as response:
        return await response.text()

async def get_current_datetime():
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: Dict[str, Any], websocket: WebSocket):
        await websocket.send_json(message)


manager = ConnectionManager()


@app.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Initialize the language model
    llm = ChatOpenAI(temperature=0.1, base_url="http://192.168.1.2:1234/v1", api_key="a", model="hermes-2-pro-mistral-7b")

    # Create tools
    tools = [
        StructuredTool.from_function(
            func=find_hotels,
            name="find_hotels",
            description="Find hotels in a city for given dates and number of guests"
        ),
        StructuredTool.from_function(
            func=get_current_datetime,
            name="get_current_datetime",
            description="Get current local datetime"
        ),
        StructuredTool.from_function(
            func=find_hotel_comments,
            name="find_hotel_comments",
            description="Find comments of hotel by its id"
        ),
    ]
    tools_map = {tool.name: tool for tool in tools}

    # Bind the tools to the language model
    llm_with_tools = llm.bind_tools(tools)

    # Initialize conversation history
    messages = []
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            user_input = data.get("message", "")
            
            # Add user message to history
            messages.append(HumanMessage(content=user_input))
            
            # Send acknowledgment of user message
            await manager.send_message(
                {"type": "user_message", "content": user_input}, 
                websocket
            )
            
            # Process with LLM and handle tool calls until we get a final response
            while True:
                # Get LLM response
                llm_response = await llm_with_tools.ainvoke(messages)
                
                # Check for tool calls
                tool_calls = llm_response.additional_kwargs.get('tool_calls', [])
                
                # If no tool calls, we have our final response
                if not tool_calls:
                    await manager.send_message(
                        {"type": "ai_message", "content": llm_response.content},
                        websocket
                    )
                    messages.append(llm_response)
                    break
                
                # Process each tool call
                messages.append(llm_response)
                
                for tool_call in tool_calls:
                    tool_name = tool_call.get('function', {}).get('name')
                    
                    # Notify client about tool execution
                    await manager.send_message(
                        {"type": "tool_start", "name": tool_name},
                        websocket
                    )
                    
                    if tool_name in tools_map:
                        tool = tools_map[tool_name]
                        
                        # Parse arguments
                        args_str = tool_call.get('function', {}).get('arguments', '{}')
                        args = json.loads(args_str)
                        
                        # Execute the tool
                        tool_result = await tool.invoke(args)
                        
                        # Notify client about tool result
                        await manager.send_message(
                            {"type": "tool_result", "name": tool_name, "result": tool_result},
                            websocket
                        )
                        
                        # Add tool result to message history
                        tool_message = ToolMessage(
                            content=json.dumps(tool_result) if isinstance(tool_result, (dict, list)) else str(tool_result),
                            tool_call_id=tool_call.get('id')
                        )
                        messages.append(tool_message)
                    else:
                        error_msg = f"Error: Tool '{tool_name}' not found"
                        
                        # Notify client about error
                        await manager.send_message(
                            {"type": "tool_error", "name": tool_name, "error": error_msg},
                            websocket
                        )
                        
                        # Add error message as tool result
                        tool_message = ToolMessage(
                            content=error_msg,
                            tool_call_id=tool_call.get('id')
                        )
                        messages.append(tool_message)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/")
async def root():
    return {"message": "Hotel Chat API is running"}


if __name__ == "__main__":
    uvicorn.run("weather:app", host="0.0.0.0", port=8080, reload=True)

