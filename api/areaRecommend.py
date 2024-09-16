import random
import requests
import xml.etree.ElementTree as ET
import pandas as pd
import chardet
from flask import jsonify

import os
from dotenv import load_dotenv

load_dotenv()
# 구글 맵 API 키
google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')
google_url = os.getenv('GOOGLE_URL')

area_url = os.getenv('AREA_API_URL')
area_key = os.getenv('AREA_API_KEY')


def fetch_location_data(areaCd, signguCd):
    url = f'{area_url}?serviceKey={area_key}&numOfRows=20&pageNo=1&MobileOS=ETC&MobileApp=AppTest&baseYm=202408&areaCd={areaCd}&signguCd={signguCd}'
    print("요청 URL:", url)
    # print("요청 파라미터:", params)
    try:
        response = requests.get(url)
        response.raise_for_status()

        # 응답 데이터의 인코딩을 감지하여 설정
        detected_encoding = chardet.detect(response.content)['encoding']
        response.encoding = detected_encoding

        # 응답 데이터의 일부를 출력하여 디버깅
        # print("응답 데이터 일부:", response.text[:500])

        return response.text
    except requests.RequestException as e:
        print(f"API 요청 오류: {e}")
        return None
    except Exception as e:
        print(f"예기치 않은 오류 발생: {e}")
        return None

def parse_xml_and_filter(xml_data):
    filtered_items = []
    try:
        root = ET.fromstring(xml_data)
        items = root.find('.//items')

        if items is None:
            print("items 태그를 찾을 수 없습니다.")
            return filtered_items

        for item in items.findall('item'):
            hubCtgryMclsNm = item.find('hubCtgryMclsNm')
            hubRank = item.find('hubRank')
            hubTatsNm = item.find('hubTatsNm')

            if hubCtgryMclsNm is not None and hubRank is not None and hubTatsNm is not None:
                hubCtgryMclsNm_text = hubCtgryMclsNm.text
                hubRank_value = int(hubRank.text)
                hubTatsNm_text = hubTatsNm.text

                if hubCtgryMclsNm_text == "문화관광" and hubRank_value <= 20:
                    # Element가 아닌 딕셔너리로 데이터를 변환하여 추가
                    filtered_items.append({
                        'hubCtgryMclsNm': hubCtgryMclsNm_text,
                        'hubRank': hubRank_value,
                        'hubTatsNm': hubTatsNm_text
                    })

    except ET.ParseError as e:
        print(f"XML 파싱 오류: {e}")
    except Exception as e:
        print(f"예기치 않은 오류 발생: {e}")
    return filtered_items


def find_matching_area(input_value, csv_path):
    # areaNm과 sigunguNm을 모두 검사
    df = pd.read_csv(csv_path, encoding='utf-8')

    # areaNm에서 첫 번째 일치하는 값 찾기
    for index, row in df.iterrows():
        if input_value in row['areaNm']:
            return pd.DataFrame([{'areaCd': row['areaCd'], 'sigunguCd': row['sigunguCd']}])

    # areaNm에서 일치하는 값이 없을 경우 sigunguNm에서 찾기
    for index, row in df.iterrows():
        if input_value in row['sigunguNm']:
            return pd.DataFrame([{'areaCd': row['areaCd'], 'sigunguCd': row['sigunguCd']}])

    # 일치하는 값이 없는 경우 빈 DataFrame 반환
    return pd.DataFrame()

def process_area(input_value):
    matching_area = find_matching_area(input_value, 'areaCode.csv')

    if not matching_area.empty:
        all_filtered_items = []
        for _, row in matching_area.iterrows():
            areaCd = row['areaCd']
            sigunguCd = row['sigunguCd']
            xml_data = fetch_location_data(areaCd, sigunguCd)
            if xml_data:
                filtered_items = parse_xml_and_filter(xml_data)
                all_filtered_items.extend(filtered_items)

        # Return or process filtered items as needed
        return all_filtered_items
    else:
        print("Matching area not found.")
        return []