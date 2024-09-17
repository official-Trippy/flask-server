from flask import Flask, request, jsonify
import requests

import os
from dotenv import load_dotenv

load_dotenv()

elasticsearch_url = os.getenv('ELASTICSEARCH_URL')

def search_posts_function(interest, post_type, member_idx):
    try:
        query = {
            "_source": ["post_id"],
            "query": {
                "bool": {
                    "must": [
                        {"match": {"interest": interest}},
                        {"match": {"post_type": post_type}}
                    ],
                    "must_not": [
                        {"term": {"member_idx": member_idx}}
                    ]
                }
            }
        }

        response = requests.post(f"{elasticsearch_url}/mysql_data_index/_search", json=query)
        response.raise_for_status()  # HTTP 에러 체크

        es_data = response.json()
        post_ids = [hit['_source']['post_id'] for hit in es_data['hits']['hits']]

        return post_ids

    except requests.exceptions.RequestException as e:
        raise Exception(f"Error connecting to Elasticsearch: {e}")
    except Exception as e:
        raise Exception(f"Unexpected error occurred: {e}")