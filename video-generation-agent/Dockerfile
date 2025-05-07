# # Dockerfile
# FROM python:3.10.13-slim

# # 작업 디렉토리 설정
# WORKDIR /app

# # 시스템 의존성 설치 (SpaCy 빌드를 위한)
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     gcc \
#     g++ \
#     && rm -rf /var/lib/apt/lists/*

# # requirements.txt 복사 및 의존성 설치
# COPY requirements.txt .
# RUN pip install --no-cache-dir --upgrade pip setuptools wheel
# RUN pip install --no-cache-dir -r requirements.txt

# # SpaCy 모델 다운로드
# RUN python -m spacy download en_core_web_sm
# RUN python -m spacy download ko_core_news_sm

# # 애플리케이션 코드 복사
# COPY . .

# # 포트 노출
# EXPOSE 8501

# # 환경 변수 설정
# ENV PYTHONUNBUFFERED=1
# ENV PYTHONDONTWRITEBYTECODE=1

# # 헬스체크 설정
# HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# # 실행 명령
# CMD ["streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]

FROM python:3.10.13-slim

WORKDIR /app

# 시스템 종속성 설치
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# pip를 통해 OpenCV 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir -r requirements.txt

# SpaCy 모델 설치 (한국어/영어 병렬 설치)
RUN python -m spacy download en_core_web_sm && \
    python -m spacy download ko_core_news_sm

# 애플리케이션 코드 복사
COPY src/ ./src/
# COPY .env /app/.env

# 디렉토리 구조 생성
RUN mkdir -p /app/data/{videos,cache,history} && \
    mkdir -p /app/logs

EXPOSE 8501

# 실행 명령
CMD ["streamlit", "run", "src/main.py", "--server.port=8501", "--server.address=0.0.0.0"]