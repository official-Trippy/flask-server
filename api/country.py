import os
from dotenv import load_dotenv

import requests
import googlemaps

# .env 파일 로드
load_dotenv()

country_url = os.getenv('COUNTRY_API_URL')
country_key = os.getenv('COUNTRY_API_KEY')

google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
google_url = os.getenv('GOOGLE_URL')


gmaps = googlemaps.Client(key=google_maps_api_key)

def get_country_data(country_name=None):
    url = f'{country_url}?serviceKey={country_key}&pageNo=1&numOfRows=10&cond[country_nm::EQ]={country_name}'
    response = requests.get(url)
    return response


def get_full_address(location):
    # Geocoding API 요청
    geocode_result = gmaps.geocode(location)

    if not geocode_result:
        return None

    # 첫 번째 결과에서 주소 구성 요소 추출
    address_components = geocode_result[0]['address_components']

    # 국가 정보 찾기
    country_name = None
    for component in address_components:
        if 'country' in component['types']:
            country_name = component['short_name']
            break

    get_country_data(country_name)

    return country_name