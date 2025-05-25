import uvicorn
from fastapi import FastAPI, Query
from typing import Dict
from src.managers.hotels_manager import get_city, get_hotels_for_city, find_comments

app = FastAPI()

@app.get("/search-city")
async def search_city(city: str = Query(..., description="Name of the city")) -> Dict[str, object]:
    city_data = await get_city(city)

    return {
        "cityId": city_data[0],
        "cityName": city_data[1]
    }


@app.get("/find-hotels-of-city")
async def find_hotels_of_city(cityId: int = Query(..., description="ID of the city"),
                              cityName: str = Query(..., description="Name of the city"),
                              checkInDate: str = Query(..., description="Check in date ISO"),
                              checkOutDate: str = Query(..., description="Check out date ISO"),
                              adultsCount: int = Query(..., description="Number of adults"),
                              childrenCount: int = Query(..., description="Number of children"),
                              ) -> list[Dict[str, object]]:
    return await get_hotels_for_city(city_code=cityId, city_name=cityName, check_in_date=checkInDate, check_out_date=checkOutDate, adults_count=adultsCount, children_count=childrenCount)

@app.get("/get-comments-by-hotel")
async def find_hotels_of_city(hotelId: int) -> list[Dict[str, object]]:
    return await find_comments(hotelId)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
