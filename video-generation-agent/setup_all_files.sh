#!/bin/bash

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up Video Generation Agent files...${NC}"

# Dockerfile을 루트로 이동
echo -e "${YELLOW}Moving Dockerfile to root...${NC}"
mv docker/Dockerfile ./
mv docker/docker-compose.yml ./

# .dockerignore 생성
echo -e "${YELLOW}Creating .dockerignore...${NC}"
cat > .dockerignore << 'EOL'
venv/
.venv/
**/__pycache__
**/*.pyc
.git
.gitignore
.env
!.env.example
logs/*
data/cache/*
data/history/*
data/videos/*
tests/
docs/
**/.DS_Store
README.md
EOL

# .env.example 생성
echo -e "${YELLOW}Creating .env.example...${NC}"
cat > .env.example << 'EOL'
# Application
APP_NAME=Video Generation Agent
APP_ENV=development
DEBUG=True

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# MongoDB Configuration
MONGODB_URL=mongodb://admin:password@mongodb:27017
MONGODB_DB=video_agent

# External APIs (empty for mock mode)
VIDEO_API_KEY=
VIDEO_API_ENDPOINT=

# Monitoring
PROMETHEUS_PORT=9090
EOL

# .env 파일 생성
echo -e "${YELLOW}Creating .env file...${NC}"
cp .env.example .env

# src/config/settings.py 생성
echo -e "${YELLOW}Creating config/settings.py...${NC}"
cat > src/config/settings.py << 'EOL'
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    APP_NAME = os.getenv("APP_NAME", "Video Generation Agent")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "True") == "True"
    
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    
    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    
    MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DB = os.getenv("MONGODB_DB", "video_agent")
    
    VIDEO_API_KEY = os.getenv("VIDEO_API_KEY")
    VIDEO_API_ENDPOINT = os.getenv("VIDEO_API_ENDPOINT")

settings = Settings()
EOL

# src/config/logging.py 생성
echo -e "${YELLOW}Creating config/logging.py...${NC}"
cat > src/config/logging.py << 'EOL'
import logging
import structlog
from pathlib import Path

def setup_logging():
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        format="%(message)s",
        level=logging.INFO
    )
    
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.format_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )
    
    return structlog.get_logger()
EOL

# src/main.py 생성
echo -e "${YELLOW}Creating main.py...${NC}"
cat > src/main.py << 'EOL'
import streamlit as st
from config.settings import settings
from config.logging import setup_logging

logger = setup_logging()

def main():
    st.set_page_config(
        page_title=settings.APP_NAME,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎬 프롬프트 최적화 영상 생성 에이전트")
    
    # 개발 중 표시
    st.info("시스템 개발 중입니다. Docker 환경이 정상적으로 실행되었습니다.")
    
    # 간단한 테스트 UI
    st.header("시스템 상태")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("환경", settings.APP_ENV)
        st.metric("디버그 모드", str(settings.DEBUG))
    
    with col2:
        st.metric("Redis 호스트", settings.REDIS_HOST)
        st.metric("MongoDB DB", settings.MONGODB_DB)
    
    # 로깅 테스트
    if st.button("테스트 로그 생성"):
        logger.info("test_log", message="Docker 환경에서 로깅 테스트")
        st.success("로그가 생성되었습니다.")

if __name__ == "__main__":
    main()
EOL

# 최소한의 component 파일들 생성
echo -e "${YELLOW}Creating minimal component files...${NC}"

# Cache manager
cat > src/components/cache/cache_manager.py << 'EOL'
import redis
from config.settings import settings

class CacheManager:
    def __init__(self):
        self.redis_client = None
        
    def connect(self):
        try:
            self.redis_client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB
            )
            self.redis_client.ping()
            return True
        except Exception as e:
            print(f"Redis connection failed: {e}")
            return False
EOL

# Prompt generator
cat > src/components/prompt_generator/generator.py << 'EOL'
class PromptGenerator:
    def __init__(self):
        pass
    
    async def generate_prompt(self, user_input: str):
        # 기본 구현
        return {
            "original_input": user_input,
            "optimized_prompt": f"Generate video: {user_input}",
            "metadata": {}
        }
EOL

# Prompt editor
cat > src/components/prompt_editor/editor.py << 'EOL'
class PromptEditor:
    def __init__(self):
        pass
    
    def generate_diff(self, original: str, modified: str):
        # 기본 구현
        return {
            "original": original,
            "modified": modified,
            "changes": []
        }
EOL

# Video generator
cat > src/components/video_generator/generator.py << 'EOL'
class VideoGenerator:
    def __init__(self):
        pass
    
    async def generate(self, prompt: str):
        # Mock 구현
        return {
            "video_id": "mock_video_1",
            "video_url": "/placeholder/video.mp4",
            "resolution": "720p",
            "duration": 10,
            "created_at": "2024-01-01T00:00:00"
        }
EOL

# Error handler
cat > src/components/error_handling/handler.py << 'EOL'
class ErrorHandler:
    def __init__(self):
        pass
    
    def handle_error(self, error):
        print(f"Error: {error}")
        return {"error_id": "mock_error", "message": str(error)}
EOL

# Monitor
cat > src/components/monitoring/monitor.py << 'EOL'
class Monitor:
    def __init__(self):
        pass
    
    def collect_metrics(self):
        # Mock implementation
        return {"status": "ok", "metrics": {}}
EOL

# __init__.py 파일들도 간단한 내용 추가
echo -e "${YELLOW}Adding content to __init__.py files...${NC}"
echo "# Video Generation Agent" > src/__init__.py
echo "# Components" > src/components/__init__.py
echo "# Config" > src/config/__init__.py
echo "# Utils" > src/utils/__init__.py
echo "# Monitoring" > src/monitoring/__init__.py

# requirements.txt 업데이트
echo -e "${YELLOW}Updating requirements.txt...${NC}"
cat > requirements.txt << 'EOL'
# Core Dependencies
streamlit==1.45.0
python-dotenv==1.0.0

# Database and Caching
redis==5.0.1
pymongo==4.5.0

# Monitoring & Logging
prometheus-client==0.19.0
structlog==24.1.0

# HTTP & API
requests==2.31.0
aiohttp==3.9.1

# Basic NLP (no SpaCy for now)
nltk==3.8.1

# Testing
pytest==7.4.4
pytest-asyncio==0.23.2

# Utils
python-dateutil==2.8.2
EOL

echo -e "${GREEN}Setup complete! You can now run:${NC}"
echo -e "${YELLOW}docker build -t video-agent .${NC}"
echo -e "${YELLOW}docker-compose up -d${NC}"
echo -e "${YELLOW}docker-compose logs -f${NC}"
echo -e "\nThe application will be available at: http://localhost:8501"