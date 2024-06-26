from flask import Blueprint, request, jsonify, Response
import json
from .weather import get_weather_list, get_nearest_location, read_branch, check_country, get_weather_info
from response_dto import ReasonDTO, ErrorReasonDTO

api_bp = Blueprint('api', __name__)

@api_bp.route('/weather', methods=['GET'])
def weather():
    try:
        # 입력 파라미터 가져오기
        latitude = float(request.args.get('latitude'))
        longitude = float(request.args.get('longitude'))
        date = request.args.get('date')

        # 국가 확인
        if check_country(latitude, longitude) != "South Korea":
            dto = ErrorReasonDTO(False, "NATION4001", "NO_PERMISSION_NATION")
            return jsonify(dto.__dict__), 403

        # 가장 가까운 위치의 관측소 찾기
        branches = read_branch('data/branchInfo.csv')
        nearest_branch = get_nearest_location(branches, latitude, longitude)

        # 날씨 정보 요청
        weather_response = get_weather_list(nearest_branch['branch'], date)
        if weather_response.status_code != 200:
            dto = ErrorReasonDTO(False, "WEATHER4002", "ERROR_WHILE_GET_WEATHER")
            return jsonify(dto.__dict__), 500

        # 날씨 데이터 추출 및 처리
        weather_data = weather_response.json()['response']['body']['items']['item']
        result = get_weather_info(weather_data)

        # 성공적인 응답
        dto = ReasonDTO(True, "COMMON200", "SUCCESS", result)
        return jsonify(dto.__dict__), 200

    except Exception as e:
        # 예외 처리
        error_msg = f"Unexpected error occurred: {str(e)}"
        dto = ErrorReasonDTO(False, "COMMON500", "INTERNAL_SERVER_ERROR", error_msg)
        return jsonify(dto.__dict__), 500
