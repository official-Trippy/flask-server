from flask import Blueprint, request, jsonify, Response
import json
from .weather import get_weather_list, get_nearest_location, read_branch, check_country, get_weather_info
from response_dto import ReasonDTO, ErrorReasonDTO
from .country import get_country_data, get_full_address
from urllib.parse import unquote
from .areaRecommend import process_area
from .interestPost import search_posts_function

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
        print(error_msg)
        dto = ErrorReasonDTO(False, "COMMON500", "INTERNAL_SERVER_ERROR", error_msg)
        return "500"

@api_bp.route('/location', methods=['GET'])
def location():
    try:
        location = request.args.get('location')
        if location:
            decoded_location = unquote(location)
            print(f"location: {decoded_location}")  # 디버깅을 위한 로그 추가
            data = get_full_address(decoded_location)
            return data
        else:
            return jsonify({
                'success': False,
                'error_code': 'COMMON400',
                'message': 'BAD_REQUEST',
                'detail': 'Location parameter is missing'
            }), 400
    except Exception as e:
        # 예외 처리
        error_msg = f"Unexpected error occurred: {str(e)}"
        print(error_msg)
        return jsonify({
            'success': False,
            'error_code': 'COMMON500',
            'message': 'INTERNAL_SERVER_ERROR',
            'detail': error_msg
        }), 500
#
# @api_bp.route('/recommend/post', methods=['POST'])
# def recommend():
#     try:
#         # jpype.attachThreadToJVM()
#         data = request.get_json()
#         print("Received data:", data)  # 데이터를 디버깅하기 위한 로그
#
#         # 데이터 처리 로직 작성
#         extracted_keywords = extract_keyword(data)
#
#         # 결과 출력'
#         result = ','.join(extracted_keywords)
#         print(result)
#         return Response(result, content_type='text/plain; charset=utf-8')
#         # print(f"Extracted Keywords: {', '.join(extracted_keywords)}")  # 전체 키워드를 출력
#         #
#         # return jsonify({"message": "Recommendation processed"}), 200
#     except Exception as e:
#         # 예외 처리
#         error_msg = f"Unexpected error occurred: {str(e)}"
#         return jsonify({
#             'success': False,
#             'error_code': 'COMMON500',
#             'message': 'INTERNAL_SERVER_ERROR',
#             'detail': error_msg
#         }), 500

@api_bp.route('/find_area', methods=['GET'])
def find_area():
    try:
        input_value = request.args.get('input')
        decoded_input = unquote(input_value)
        # print(f"Received input (decoded): {decoded_input}")
        if not input_value:
            return jsonify({
                'success': False,
                'error_code': 'COMMON400',
                'message': 'BAD_REQUEST',
                'detail': 'Input parameter is missing'
            }), 400

        # 지역 검색 및 필터링된 데이터 가져오기
        matching_results = process_area(decoded_input)

        if not matching_results:
            return jsonify({
                'success': False,
                'error_code': 'DATA_NOT_FOUND',
                'message': 'No matching data found'
            }), 404

        # JSON 직렬화 가능한 형태로 반환
        # print("Matching Results:", matching_results)
        return jsonify(matching_results)

    except Exception as e:
        error_msg = f"Unexpected error occurred: {str(e)}"
        print(error_msg)
        return jsonify({
            'success': False,
            'error_code': 'COMMON500',
            'message': 'INTERNAL_SERVER_ERROR',
            'detail': error_msg
        }), 500

@api_bp.route('/interest_posts', methods=['GET'])
def interest_posts():
    try:
        # 쿼리 파라미터로 interest와 post_type 받기
        interest = request.args.get('interest')
        post_type = request.args.get('post_type')
        member_idx = request.args.get('member_idx')

        if not interest or not post_type:
            return jsonify({
                'success': False,
                'error_code': 'COMMON400',
                'message': 'BAD_REQUEST',
                'detail': 'Interest or post_type parameter is missing'
            }), 400

        # Elasticsearch에 요청 보내기
        post_ids = search_posts_function(interest, post_type, member_idx)

        return jsonify({
            'success': True,
            'post_ids': post_ids
        })

    except Exception as e:
        print(error_msg)
        return jsonify({
            'success': False,
            'error_code': 'COMMON500',
            'message': 'INTERNAL_SERVER_ERROR',
            'detail': str(e)
        }), 500