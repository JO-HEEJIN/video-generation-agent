# 프롬프트 편집기 코드
import difflib
import json
from datetime import datetime
from typing import Dict, List, Any

class PromptEditor:
    def __init__(self):
        self.edit_history = []
    
    def generate_diff(self, original: str, modified: str) -> Dict[str, Any]:
        """원본과 수정된 프롬프트 간의 차이 생성"""
        # diff 생성
        diff = difflib.ndiff(original.split(), modified.split())
        
        # 변경 사항 분석
        changes = []
        for i, line in enumerate(diff):
            if line.startswith('- '):
                # 삭제된 단어
                changes.append({
                    "type": "removed",
                    "position": i,
                    "content": line[2:]
                })
            elif line.startswith('+ '):
                # 추가된 단어
                changes.append({
                    "type": "added",
                    "position": i,
                    "content": line[2:]
                })
        
        # 변경 사항 요약
        summary = self._generate_summary(changes, original, modified)
        
        # 최종 결과
        result = {
            "timestamp": datetime.now().isoformat(),
            "original": original,
            "modified": modified,
            "changes": changes,
            "summary": summary
        }
        
        # 이력 저장
        self.edit_history.append(result)
        
        return result
    
    def _generate_summary(self, changes: List[Dict], original: str, modified: str) -> Dict[str, Any]:
        """변경 사항 요약 생성"""
        added = len([c for c in changes if c["type"] == "added"])
        removed = len([c for c in changes if c["type"] == "removed"])
        
        # 변경 유형 분석
        change_types = []
        if added > removed and added > 0:
            change_types.append("세부 정보 추가")
        if removed > added and removed > 0:
            change_types.append("단순화")
        if added > 0 and removed > 0:
            change_types.append("내용 변경")
        if added == 0 and removed == 0:
            change_types.append("변경 없음")
        
        # 단어 수 변화
        word_count_diff = len(modified.split()) - len(original.split())
        
        return {
            "total_changes": added + removed,
            "added_words": added,
            "removed_words": removed,
            "change_types": change_types,
            "word_count_diff": word_count_diff,
            "improved": word_count_diff > 0  # 단어 수 증가를 개선으로 간주
        }
    
    def get_edit_history(self) -> List[Dict[str, Any]]:
        """편집 이력 반환"""
        return self.edit_history