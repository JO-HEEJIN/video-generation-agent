# src/components/history/history_manager.py
import json
from datetime import datetime
from typing import List, Dict, Optional
from pymongo import MongoClient
from config.settings import settings
from pathlib import Path

class HistoryManager:
    def __init__(self):
        self.history_dir = Path(settings.DATA_DIR) / "history"
        self.history_dir.mkdir(exist_ok=True, parents=True)
        
        # MongoDB 연결 설정
        if settings.MONGODB_URL:
            self.client = MongoClient(settings.MONGODB_URL)
            self.db = self.client[settings.MONGODB_DB]
            self.collection = self.db["prompt_history"]
        else:
            self.collection = None

    def save_history(self, entry: Dict) -> None:
        """히스토리 항목 저장"""
        entry['timestamp'] = datetime.now().isoformat()
        
        # MongoDB 저장
        if self.collection is not None:
            try:
                self.collection.insert_one(entry)
            except Exception as e:
                print(f"MongoDB 저장 실패: {e}, 로컬에 백업 저장")
                self._save_to_local(entry)
        else:
            self._save_to_local(entry)

    def _save_to_local(self, entry: Dict) -> None:
        """로컬 파일 시스템에 저장"""
        filename = f"history_{datetime.now().strftime('%Y%m%d%H%M%S')}.json"
        filepath = self.history_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False)

    def get_recent_history(self, limit: int = 5) -> List[Dict]:
        """최근 히스토리 조회"""
        if self.collection is not None:
            try:
                return list(self.collection.find().sort("timestamp", -1).limit(limit))
            except Exception as e:
                print(f"MongoDB 조회 실패: {e}, 로컬에서 로드")
                return self._load_from_local(limit)
        return self._load_from_local(limit)

    def _load_from_local(self, limit: int) -> List[Dict]:
        """로컬 파일 시스템에서 로드"""
        files = sorted(self.history_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        history = []
        for file in files[:limit]:
            with open(file, 'r', encoding='utf-8') as f:
                history.append(json.load(f))
        return history

    def find_similar_prompts(self, query: str, threshold: float = 0.7) -> List[Dict]:
        """유사한 프롬프트 검색 (간단한 키워드 매칭)"""
        all_entries = self.get_recent_history(limit=100)
        query_keywords = set(query.lower().split())
        
        similar = []
        for entry in all_entries:
            entry_keywords = set(entry['input'].lower().split())
            intersection = query_keywords.intersection(entry_keywords)
            similarity = len(intersection) / max(len(query_keywords), 1)
            if similarity >= threshold:
                similar.append(entry)
        return similar