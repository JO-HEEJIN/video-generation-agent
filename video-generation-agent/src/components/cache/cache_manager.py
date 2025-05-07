# import redis
# from config.settings import settings

# class CacheManager:
#     def __init__(self):
#         self.redis_client = None
        
#     def connect(self):
#         try:
#             self.redis_client = redis.Redis(
#                 host=settings.REDIS_HOST,
#                 port=settings.REDIS_PORT,
#                 db=settings.REDIS_DB
#             )
#             self.redis_client.ping()
#             return True
#         except Exception as e:
#             print(f"Redis connection failed: {e}")
#             return False


# src/components/cache/cache_manager.py
import redis
import json
from datetime import timedelta
from config.settings import settings
from typing import Optional, Dict, Any

class CacheManager:
    def __init__(self):
        self.redis = None
        if settings.REDIS_HOST:
            try:
                # 패스워드 옵션 조건부 설정
                password = getattr(settings, 'REDIS_PASSWORD', None)
                self.redis = redis.Redis(
                    host=settings.REDIS_HOST,
                    port=settings.REDIS_PORT,
                    db=settings.REDIS_DB,
                    password=password,  # None이면 패스워드 없이 연결
                    decode_responses=True
                )
                self.redis.ping()  # 연결 테스트
            except redis.ConnectionError:
                self.redis = None

    def get(self, key: str) -> Optional[Dict]:
        """캐시에서 데이터 가져오기"""
        if not self.redis:
            return None
            
        data = self.redis.get(key)
        return json.loads(data) if data else None

    def set(self, key: str, value: Dict, ttl: int = 3600) -> bool:
        """캐시에 데이터 저장"""
        if not self.redis:
            return False
            
        try:
            self.redis.setex(key, timedelta(seconds=ttl), json.dumps(value))
            return True
        except Exception as e:
            print(f"캐시 저장 실패: {e}")
            return False

    def delete(self, key: str) -> None:
        """캐시 데이터 삭제"""
        if self.redis:
            self.redis.delete(key)