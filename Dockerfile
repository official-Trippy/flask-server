# 베이스 이미지로 Python 3.9 사용
FROM python:3.9

# 작업 디렉토리 설정
WORKDIR /app

# 필요한 파일들을 컨테이너 내부로 복사
COPY requirements.txt requirements.txt
COPY . .

# 필요한 패키지 설치
RUN pip install --no-cache-dir -r requirements.txt

# JVM 설치 (OpenJDK 11)
RUN apt-get update && apt-get install -y openjdk-11-jre-headless

# 환경 변수 설정 (필요시)
ENV JAVA_OPTS="-Xmx1024m -Xms512m"

# Flask 서버 실행
CMD ["flask", "run", "--host=0.0.0.0"]
