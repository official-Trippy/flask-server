import csv
from math import radians, sin, cos, sqrt, atan2
import pandas as pd

def read_branch(csv_path):

    branches_df = pd.read_csv(csv_path, encoding='utf-8')
    branches_list = []
    for index, row in branches_df.iterrows():
        branch_info = {
            'branch': row['지점'],
            'branchName': row['지점명'],
            'latitude': float(row['좌표'].split(',')[0].strip()),
            'longitude': float(row['좌표'].split(',')[1].strip())
        }
        branches_list.append(branch_info)

    return branches_list

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

