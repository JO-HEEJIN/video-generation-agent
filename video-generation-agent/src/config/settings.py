# import os
# from pathlib import Path
# from dotenv import load_dotenv

# load_dotenv()

# class Settings:
#     APP_NAME = os.getenv("APP_NAME", "Video Generation Agent")
#     APP_ENV = os.getenv("APP_ENV", "development")
#     DEBUG = os.getenv("DEBUG", "True") == "True"
    
#     BASE_DIR = Path(__file__).resolve().parent.parent.parent
#     DATA_DIR = BASE_DIR / "data"
#     LOGS_DIR = BASE_DIR / "logs"
    
#     REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
#     REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
#     REDIS_DB = int(os.getenv("REDIS_DB", 0))
    
#     MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
#     MONGODB_DB = os.getenv("MONGODB_DB", "video_agent")
    
#     VIDEO_API_KEY = os.getenv("VIDEO_API_KEY")
#     VIDEO_API_ENDPOINT = os.getenv("VIDEO_API_ENDPOINT")

# settings = Settings()
# src/config/settings.py (수정 버전)
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # 기본 설정
    APP_NAME = os.getenv("APP_NAME", "Video Generation Agent")
    APP_ENV = os.getenv("APP_ENV", "development")
    DEBUG = os.getenv("DEBUG", "True") == "True"
    
    # 경로 설정
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    DATA_DIR = BASE_DIR / "data"
    LOGS_DIR = BASE_DIR / "logs"
    
    # Redis 설정
    REDIS_HOST = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    
    # MongoDB 설정
    MONGODB_URL = os.getenv(
        "MONGODB_URL", 
        "mongodb://admin:password@mongodb:27017/video_agent?authSource=admin"
    )
    MONGODB_DB = os.getenv("MONGODB_DB", "video_agent")
    
    # 영상 API 설정
    VIDEO_API_KEY = os.getenv("VIDEO_API_KEY", "mock_key")
    VIDEO_API_ENDPOINT = os.getenv("VIDEO_API_ENDPOINT", "http://mock-api/v1")

settings = Settings()