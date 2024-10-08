from dataclasses import dataclass, field
from typing import List
from sklearn.feature_extraction.text import TfidfVectorizer
import requests

# 연속된 문자열 제거 함수
def remove_consecutive_words(s):
    result = []
    count = 1

    if s:
        result.append(s[0])

    for i in range(1, len(s)):
        if s[i] == s[i-1]:
            count += 1
        else:
            count = 1

        if count < 3:
            result.append(s[i])

    return ''.join(result)

# 길이가 긴 단어를 강제로 분리하는 함수
def insert_spaces(input_string, max_word_length=20):
    words = input_string.split()

    for i, word in enumerate(words):
        if len(word) >= max_word_length:
            split_words = [word[j:j+max_word_length] for j in range(0, len(word), max_word_length)]
            words[i] = '. '.join(split_words)

    result_string = ' '.join(words)
    return result_string

# 텍스트 전처리 및 형태소 분석 API 호출 함수
def tokenizing(sentence):
    sentence = insert_spaces(sentence.lower())
    sentence = remove_consecutive_words(sentence)

    try:
        response = requests.post(
            "https://trippy-api.store/pylocal/analyze",
            json={"text": sentence},
        )
        # 상태 코드 확인
        #print(f"Response status code: {response.status_code}")
        #print(f"Response content: {response.text}")

        if response.status_code == 200:
            result = response.json()
            # 형태소 분석 결과에서 명사만 추출 (NNG: 일반 명사, NNP: 고유 명사)
            tokens = [morph[0] for morph in result.get('morphs', []) if morph[1].startswith('NN')]
            #print(f"Response tokens: {tokens}")  # 응답에서 추출한 명사를 출력
        else:
            print(f"Error: Received status code {response.status_code}")
            tokens = []

    except requests.exceptions.RequestException as e:
        # 요청 중 발생한 예외를 처리
        print(f"Error during the API request: {e}")
        tokens = []

    # 길이 1 이하 토큰 및 숫자 제거
    tokens = [x for x in tokens if len(x) > 1]
    tokens = [x for x in tokens if not x.isdigit()]

    return tokens


# GetRecommendRequest를 받아서 TF-IDF 기반으로 키워드를 추출하는 함수
def extract_keyword(data: dict, top_n: int = 5) -> List[str]:
    documents = []

    # likePostContentDtoList와 popularPostContentDtoList에서 제목과 내용을 전처리 후 추가
    if 'likePostContentDtoList' in data and data['likePostContentDtoList']:
        for post in data['likePostContentDtoList']:
            tokens = tokenizing(f"{post['title']} {post['body']}")
            if tokens:  # 토큰이 있는 경우에만 추가
                #print(f"Tokenized post: {tokens}")  # 토큰화된 결과를 출력
                documents.append(' '.join(tokens))

    if 'popularPostContentDtoList' in data and data['popularPostContentDtoList']:
        for post in data['popularPostContentDtoList']:
            tokens = tokenizing(f"{post['title']} {post['body']}")
            if tokens:  # 토큰이 있는 경우에만 추가
                #print(f"Tokenized popular post: {tokens}")  # 토큰화된 결과를 출력
                documents.append(' '.join(tokens))

    # popularSearchList와 currentSearchList도 추가
    if 'popularSearchList' in data and data['popularSearchList']:
        documents.append(' '.join(data['popularSearchList']))

    if 'currentSearchList' in data and data['currentSearchList']:
        documents.append(' '.join(data['currentSearchList']))

    if not documents:  # documents 리스트가 비었을 경우 에러 처리
        #print("No documents to process for TF-IDF")
        return []

    #print(f"Documents: {documents}")  # 최종 문서 리스트를 출력

    # TF-IDF 벡터라이저 설정
    vectorizer = TfidfVectorizer(tokenizer=lambda x: x.split(), analyzer='word')
    try:
        tfidf_matrix = vectorizer.fit_transform(documents)
    except ValueError as e:
        #print(f"Error during TF-IDF vectorization: {e}")
        return []

    # 전체 평균 TF-IDF 계산 및 키워드 추출
    avg_tfidf = tfidf_matrix.mean(axis=0)
    tfidf_scores = zip(vectorizer.get_feature_names_out(), avg_tfidf.tolist()[0])
    sorted_tfidf = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)

    # 상위 n개의 키워드 반환
    keywords = [word for word, score in sorted_tfidf[:top_n]]
    return keywords
