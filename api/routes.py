from flask import Blueprint, request, jsonify, Response
import json
from .weather import get_weather_list, get_nearest_location, read_branch, check_country, get_weather_info
from response_dto import ReasonDTO, ErrorReasonDTO
from .country import get_country_data, get_full_address

api_bp = Blueprint('api', __name__)

@api_bp.route('/weather', methods=['GET'])
def weather():
    try:
        # 입력 파라미터 가져오기
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        date = request.args.get('date')

        # 국가 확인
        location_info = check_country(latitude, longitude)
        if location_info['country_name'] != "South Korea":
            # dto = ErrorReasonDTO(False, "NATION4001", "NO_PERMISSION_NATION")
            return "4001"

        # 가장 가까운 위치의 관측소 찾기
        branches = read_branch('branchInfo.csv')
        nearest_branch = get_nearest_location(branches, latitude, longitude)

        # 날씨 정보 요청
        weather_response = get_weather_list(nearest_branch['branch'], date)
        if weather_response.status_code != 200:
            dto = ErrorReasonDTO(False, "WEATHER4002", "ERROR_WHILE_GET_WEATHER")
            return "500"

        # 날씨 데이터 추출 및 처리
        weather_data = weather_response.json()['response']['body']['items']['item']
        result = get_weather_info(weather_data)
        result += "," +  location_info['area']
        print(result)

        return result

    except Exception as e:
        # 예외 처리
        error_msg = f"Unexpected error occurred: {str(e)}"
        dto = ErrorReasonDTO(False, "COMMON500", "INTERNAL_SERVER_ERROR", error_msg)
        return "500"

@api_bp.route('/location', methods=['GET'])
def location():
    try:
        location = request.args.get('location')
        data = get_full_address(location)
        return data

    except Exception as e:
        # 예외 처리
        error_msg = f"Unexpected error occurred: {str(e)}"
        return jsonify({
            'success': False,
            'error_code': 'COMMON500',
            'message': 'INTERNAL_SERVER_ERROR',
            'detail': error_msg
        }), 500
