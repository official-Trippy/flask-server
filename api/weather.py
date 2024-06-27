import csv
from math import radians, sin, cos, sqrt, atan2
import pandas as pd
import requests
from dotenv import load_dotenv
import os
from flask import Flask, jsonify, request

# .env 파일 로드
load_dotenv()
# 구글 맵 API 키
google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
google_url = os.getenv('GOOGLE_URL')
weather_url = os.getenv('WEATHER_API_URL')
weather_api_key = os.getenv('WEATHER_API_KEY')

def read_branch(csv_path):

    branches_df = pd.read_csv(csv_path, encoding='utf-8')
    branches_list = []
    for index, row in branches_df.iterrows():
        branch_info = {
            'branch': row['지점'],
            'branchName': row['지점명'],
            'latitude': float(row['위도']),
            'longitude': float(row['경도'])
        }
        branches_list.append(branch_info)

    return branches_list

def check_country(latitude, longitude):
    try:
        # 구글 맵 Geocoding API 호출
        url = f'{google_url}?latlng={latitude},{longitude}&key={google_maps_api_key}'
        response = requests.get(url)
        data = response.json()
        location_info = {}

        if data['status'] == 'OK':
            # 결과에서 국가 정보 가져오기
            for result in data['results']:
                location_info['area'] = result['address_components'][3]['long_name']

                for component in result['address_components']:
                    if 'country' in component['types']:
                        country_name = component['long_name']
                        location_info['country_name'] = country_name
                        return location_info

        return jsonify({'error': 'Unable to determine country'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# 최단거리 구하기 -하버사인
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def get_nearest_location(branches,lat,lon):
    nearest_location = min(branches, key=lambda loc: haversine(lat, lon, loc['latitude'], loc['longitude']))
    return nearest_location

def get_weather_list(branch, date):
    try:
        url = f'{weather_url}?serviceKey={weather_api_key}&dataCd=ASOS&dateCd=DAY&startDt={date}&endDt={date}&dataType=JSON&stnIds={branch}'
        response = requests.get(url)
        return response
        # weather_result = data['response']['body']['items']['item']
        # result = get_weather_info(weather_result)
        # return result
    except Exception as e:
        print(f"Error fetching weather data: {e}")
        return None

def get_weather_info(weather_list):
    result = {}

    ddMes = weather_list[0]['ddMes']
    sumRn = weather_list[0]['sumRn']
    avgTca = float(weather_list[0]['avgTca'])
    avgTa =  weather_list[0]['avgTa']
    minTa = weather_list[0]['minTa']
    maxTa = weather_list[0]['maxTa']

    result['avgTemp'] = avgTa
    result['maxTemp'] = maxTa
    result['minTemp'] = minTa

    if ddMes != '' or sumRn != '':
        if sumRn != '' and float(sumRn) >= 0.1:
            result['status'] = 'rain'
        elif ddMes != '' and float(ddMes) >= 1:
            result['status'] = 'snow'
        else:
            result['status'] = 'cloudy'
    else:
        if avgTca < 6:
            result['status'] = 'sunny'
        elif 6 <= avgTca < 9:
            result['status'] = 'mostly_cloudy'
        elif 9 <= avgTca <= 10:
            result['status'] = 'cloudy'

    return result