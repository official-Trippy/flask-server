from flask import Blueprint, request, jsonify
from .weather import get_nearest_location
from .weather import  read_branch

api_bp = Blueprint('api', __name__)

@api_bp.route('/weather', methods=['GET'])
def weather():
    latitude = float(request.args.get('latitude'))
    longitude = float(request.args.get('longitude'))
    branches = read_branch('data/branchInfo.csv')
    # print(latitude,longitude)
    weather_info = get_nearest_location(branches, latitude, longitude)
    return jsonify(weather_info)