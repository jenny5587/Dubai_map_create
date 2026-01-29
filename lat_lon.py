import warnings
import requests
KAKAO_REST_API_KEY = "kakao api key"

def get_lat_lng_from_address(address: str):
    url = "https://dapi.kakao.com/v2/local/search/address.json"
    headers = {
        "Authorization": f"KakaoAK {KAKAO_REST_API_KEY}"
    }
    params = {
        "query": address
    }

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if data["documents"]:
        lat = float(data["documents"][0]["y"])
        lng = float(data["documents"][0]["x"])
        return lat, lng
    else:
        return None, None