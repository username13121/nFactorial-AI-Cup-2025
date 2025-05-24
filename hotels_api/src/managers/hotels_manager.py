import json
import re
from src import utils
from src.managers.rnet_manager import RnetManager


async def get_city(search_str: str) -> tuple[int, str]:
    rnet_client = RnetManager.init_random_proxy().rnet_client

    response_json = await utils.get_response_json(rnet_client.post(
        "https://www.trip.com/htls/getKeyWordSearch",

        json={
            "code": 0,
            "codeType": "",
            "keyWord": search_str,
            "searchType": "D",
            "scenicCode": 0,
            "cityCodeOfUser": 0,
            "searchConditions": [
                {
                    "type": "D_PROVINCE",
                    "value": "T"
                },
                {
                    "type": "SupportNormalSearch",
                    "value": "T"
                },
                {
                    "type": "DisplayTagIcon",
                    "value": "T"
                }
            ],
            "head": {
                "platform": "PC",
                "bu": "ibu",
                "group": "TRIP",
                "aid": "",
                "sid": "",
                "ouid": "",
                "caid": "",
                "csid": "",
                "couid": "",
                "region": "XX",
                "locale": "en-XX",
                "timeZone": "5",
                "currency": "USD",
                "pageID": "10320668148",
                "deviceID": "PC",
                "clientVersion": "0",

                "extension": [
                    {
                        "name": "cityId",
                        "value": "3263"
                    },
                    {
                        "name": "checkIn",
                        "value": "2025/06/01"
                    },
                    {
                        "name": "checkOut",
                        "value": "2025/06/03"
                    },
                    {
                        "name": "region",
                        "value": "XX"
                    }
                ],
                "tripSub1": "",
                "hotelExtension": {}}
        }
    ))

    if not isinstance(response_json.get("keyWordSearchResults"), list):
        raise Exception(f"invalid city: {response_json}")

    if not response_json["keyWordSearchResults"]:
        raise Exception(f"invalid city: {response_json}")

    city_name = response_json["keyWordSearchResults"][0]["city"]["enusName"]
    city_code = response_json["keyWordSearchResults"][0]["city"]["geoCode"]

    return city_code, city_name

async def get_hotels_for_city(city_code: int, city_name: str, check_in_date: str, check_out_date: str, adults_count: int, children_count: int):
    rnet_client = RnetManager.init_random_proxy().rnet_client

    check_in_date = utils.parse_date(check_in_date)
    check_out_date = utils.parse_date(check_out_date)


    params = utils.dict_to_query_params({
        "city": city_code,
        "cityName": city_name,
        "checkin": check_in_date.strftime("%Y/%m/%d"),
        "checkout": check_out_date.strftime("%Y/%m/%d"),
        "barCurr": "USD",
        "locale": "en-XX",
        "curr": "USD",
        "adult": adults_count,
        "children": children_count,
    })
    response = await rnet_client.get("https://www.trip.com/hotels/list", query=params)
    response_text = await response.text()

    response_text = utils.filter_string(response_text, "window.IBU_HOTEL=", end="}};", include_start=False, include_end=True).removesuffix(";")

    try:
        response_json = json.loads(response_text)
    except:
        raise Exception(f"json decode error: {response_text}")

    hotels_info = []

    for hotel in response_json["initData"]["firstPageList"]["hotelList"]:

        total_price = hotel["hotelBasicInfo"]["priceExplanation"]

        total_price = re.search(r'\$\d+', total_price)

        if total_price is None:
            total_price = "unavailable"
        else:
            total_price = total_price.group(0)

        advantages = []
        if hotel.get("roomTags", {}).get("advantageTags") is not None:
            for advantage in hotel["roomTags"]["advantageTags"]:
                advantages.append(advantage["tagTitle"])

        hotels_info.append({
            "hotelId": hotel["hotelBasicInfo"]["hotelId"],
            "hotelName": hotel["hotelBasicInfo"]["hotelName"],
            "hotelAddress": hotel["hotelBasicInfo"]["hotelAddress"],
            "stars": hotel["hotelStarInfo"]["star"],
            "commentsScore": hotel["commentInfo"]["commentScore"],
            "commentsCount": hotel["commentInfo"]["commenterNumber"].removesuffix("reviews").removesuffix(" "),
            "advantages": advantages,
            "totalPrice": total_price
        })
    return hotels_info

