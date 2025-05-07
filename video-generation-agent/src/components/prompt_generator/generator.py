# src/components/prompt_generator/generator.py
import structlog
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import re
from datetime import datetime
import random


logger = structlog.get_logger()

class PromptCategory(Enum):
    """프롬프트 카테고리"""
    ANIMAL = "animal"
    LANDSCAPE = "landscape"
    PERSON = "person"
    ABSTRACT = "abstract"
    OBJECT = "object"
    GENERAL = "general"

@dataclass
class ExtractedElements:
    """추출된 프롬프트 요소"""
    subject: str
    action: str
    environment: str
    style: str
    quality: str
    metadata: Dict[str, Any]

class PromptGenerator:
    def __init__(self):
        self.templates = self._load_templates()
        self.style_modifiers = self._load_style_modifiers()
        # 품질 향상 문구 최적화
        self.quality_enhancers = [
            "high quality", 
            "4K resolution", 
            "professional lighting",
            "detailed textures",
            "professional composition"
        ]
        
        # 한국어-영어 주제 매핑
        self.korean_subject_map = {
            "영상": "scene",
            "강아지": "puppy",
            "고양이": "cat",
            "사람": "person",
            "여성": "woman",
            "여자": "woman",
            "남성": "man",
            "남자": "man",
            "아이": "child",
            "아기": "baby",
            "풍경": "landscape",
            "자연": "nature",
            "숲": "forest",
            "하늘": "sky",
            "바다": "ocean",
            "도시": "city",
            "산": "mountain"
        }
        
        # 한국어 동사 매핑
        self.korean_verb_map = {
            "뛰노는": "playfully running",
            "달리는": "running",
            "걷는": "walking",
            "서있는": "standing",
            "앉아있는": "sitting",
            "움직이는": "moving",
            "하는": "doing",
            "보는": "looking",
            "먹는": "eating",
            "노는": "playing",
            "쉬는": "resting",
            "자는": "sleeping",
            "점프하는": "jumping",
            "춤추는": "dancing",
            "부르는": "singing",
            "노래하는": "singing"
        }
    
    def _load_templates(self) -> Dict[PromptCategory, Dict[str, str]]:
        """프롬프트 템플릿 로드"""
        return {
            PromptCategory.ANIMAL: {
                # 템플릿 구조 개선
                "structure": "{adjective} {animal} {action} in {environment}, {style}, {quality}",
                "keywords": ["dog", "cat", "puppy", "강아지", "고양이", "동물", "pet", "animal"]
            },
            PromptCategory.LANDSCAPE: {
                "structure": "{style} {scene_type} with {elements}, {lighting} lighting, {quality}",
                "keywords": ["landscape", "scenery", "풍경", "자연", "mountain", "ocean", "nature"]
            },
            PromptCategory.PERSON: {
                "structure": "{adjective} {subject} {doing} in {environment}, {style}, {quality}",
                "keywords": ["person", "woman", "man", "child", "baby", "people", "사람", "여성", "남성", "아이", "아기", "portrait", "character", "human"]
            },
            PromptCategory.GENERAL: {
                "structure": "{description}, {style}, {quality}",
                "keywords": []
            }
        }
    
    def _load_style_modifiers(self) -> Dict[str, List[str]]:
        """스타일 수정자 로드"""
        return {
            "bright": ["vibrant", "illuminated", "sunlit", "radiant"],
            "dark": ["moody", "dramatic", "shadowy", "atmospheric"],
            "cute": ["adorable", "charming", "endearing", "delightful"],
            "beautiful": ["stunning", "gorgeous", "elegant", "magnificent"],
            "pretty": ["lovely", "attractive", "charming", "delightful"],
            "action": ["dynamic", "energetic", "motion", "movement"],
            "calm": ["peaceful", "serene", "tranquil", "relaxing"]
        }
    
    async def generate_prompt(self, user_input: str) -> Dict[str, Any]:
        """메인 프롬프트 생성 메서드"""
        try:
            # 1. 입력 분석
            extracted = self._parse_input(user_input)
            
            # 2. 카테고리 결정
            category = self._determine_category(extracted.subject)
            
            # 3. 템플릿 적용
            template = self.templates[category]
            
            # 4. 프롬프트 구성
            optimized_prompt = self._build_prompt(extracted, template)
            
            # 5. 결과 반환
            return {
                "original_input": user_input,
                "category": category.value,
                "optimized_prompt": optimized_prompt,
                "metadata": {
                    "parsed_elements": {
                        "subject": extracted.subject,
                        "action": extracted.action,
                        "environment": extracted.environment,
                        "style": extracted.style
                    },
                    "applied_template": category.value,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            logger.error("prompt_generation_failed", error=str(e), input=user_input)
            return {
                "original_input": user_input,
                "category": "error",
                "optimized_prompt": f"Error: {str(e)}",
                "metadata": {}
            }
    
    def _parse_input(self, text: str) -> ExtractedElements:
        """입력 텍스트 파싱"""
        # 간단한 정규표현식 기반 파싱
        words = text.lower().split()
        
        # 명사, 형용사, 동사 추출
        nouns = self._extract_nouns(text)
        adjectives = self._extract_adjectives(text)
        verbs = self._extract_verbs(text)
        
        # 주요 요소 추출
        subject = self._extract_subject(nouns, adjectives)
        action = self._extract_action(verbs, text)
        environment = self._extract_environment(text)
        style = self._extract_style(adjectives, text)
        
        return ExtractedElements(
            subject=subject,
            action=action,
            environment=environment,
            style=style,
            quality="high quality",
            metadata={
                "nouns": nouns,
                "adjectives": adjectives,
                "verbs": verbs,
                "original_text": text
            }
        )
    
    def _extract_nouns(self, text: str) -> List[str]:
        """명사 추출 (간단한 패턴 기반)"""
        korean_patterns = [
            r'[가-힣]+(?=[이가]?\s|[을를]?\s|[의]\s|$)',  # 조사가 붙은 명사
            r'[가-힣]+(?=가\s)',  # '가' 주어 표시
            r'[가-힣]+(?=는\s)',  # '는' 보조사
            r'[가-힣]+(?=에서\s)',  # 장소 표시
        ]
        
        nouns = []
        for pattern in korean_patterns:
            nouns.extend(re.findall(pattern, text))
        
        # 영어 명사 추출
        english_nouns = re.findall(r'\b[A-Za-z]+\b', text)
        
        # 특정 명사 매칭 - 주요 주제어 우선 추출
        specific_nouns = {
            "영상": "영상",
            "노래": "노래",
            "여성": "여성",
            "여자": "여자", 
            "남성": "남성",
            "남자": "남자",
            "아이": "아이",
            "아기": "아기"
        }
        
        for noun, value in specific_nouns.items():
            if noun in text:
                nouns.append(value)
        
        # 중복 제거 및 정리
        all_nouns = list(set(nouns + english_nouns))
        
        return [noun for noun in all_nouns if len(noun) > 1]  # 너무 짧은 단어 제거
    
    def _extract_adjectives(self, text: str) -> List[str]:
        """형용사 추출 및 영어 매핑"""
        korean_adj_patterns = [
            r'[가-힣]+(?=한\s)',  # -한
            r'[가-힣]+(?=ㄴ\s)',   # ㅂ니다체
            r'[가-힣]+(?=은\s)',   # -은
            r'[가-힣]+(?=고\s)',   # -고
        ]
        
        # 한국어 형용사-영어 매핑 강화
        adj_mapping = {
            "귀여운": "cute",
            "예쁜": "pretty",
            "아름다운": "beautiful",
            "멋진": "cool",
            "밝은": "bright",
            "어두운": "dark",
            "화려한": "vibrant",
            "자연적인": "natural",
            "사실적인": "realistic",
            "예술적인": "artistic",
            "단순한": "minimalist",
            "행복한": "happy",
            "슬픈": "sad",
            "분위기있는": "atmospheric",
            "역동적인": "dynamic"
        }
        
        adjectives = []
        for pattern in korean_adj_patterns:
            adjectives.extend(re.findall(pattern, text))
        
        # 자주 사용되는 형용사 직접 매칭
        common_adjectives = ['귀여운', '예쁜', '아름다운', '멋진', '큰', '작은', 
                           '밝은', '어두운', '즐거운', '행복한', '슬픈', '화려한']
        
        for adj in common_adjectives:
            if adj in text:
                adjectives.append(adj)
        
        # 매핑 테이블 적용
        translated = []
        for adj in set(adjectives):  # 중복 제거
            if adj in adj_mapping:
                translated.append(adj_mapping[adj])
            else:
                translated.append(adj)
            
        return list(set(translated))  # 최종 중복 제거
    
    def _extract_verbs(self, text: str) -> List[str]:
        """동사 추출 및 영어 변환"""
        verb_patterns = [
            r'[가-힣]+(?=하는\s)',  # -하는
            r'[가-힣]+(?=하다\s)',  # -하다
            r'[가-힣]+(?=한다\s)',  # -한다
            r'[가-힣]+(?=는\s)',    # -는
            r'[가-힣]+(?=고\s)',    # -고
        ]
        
        verbs = []
        for pattern in verb_patterns:
            verbs.extend(re.findall(pattern, text))
        
        # 자주 사용되는 동사 직접 매칭
        common_verbs = [
            '뛰노는', '달리는', '걷는', '서있는', '앉아있는', 
            '움직이는', '있는', '하는', '보는', '먹는', '부르는', '노래하는'
        ]
        
        for verb in common_verbs:
            if verb in text:
                verbs.append(verb)
        
        # 동사 감지를 위한 특정 구문 검색
        special_verb_phrases = {
            "노래를 부르": "부르는",
            "노래 부르": "부르는"
        }
        
        for phrase, verb in special_verb_phrases.items():
            if phrase in text:
                verbs.append(verb)
        
        # 중복 제거, 한국어 동사를 영어로 변환
        translated_verbs = []
        for verb in set(verbs):
            if len(verb) <= 2:
                continue  # 짧은 불완전한 동사 제외
                
            # 영어 동사 변환
            if verb in self.korean_verb_map:
                translated_verbs.append(self.korean_verb_map[verb])
            else:
                translated_verbs.append(verb)
                
        return translated_verbs
    
    def _extract_subject(self, nouns: List[str], adjectives: List[str]) -> str:
        """주제 추출 및 영어 변환 강화"""
        if not nouns:
            return "scene"
        
        # 특정 주제에 대한 우선순위 매핑
        priority_nouns = ["여성", "여자", "남성", "남자", "사람", "아이", "아기"]
        for priority in priority_nouns:
            if priority in nouns:
                translated = self.korean_subject_map.get(priority, priority)
                if adjectives:
                    # 중복 방지를 위한 확인
                    adjective = adjectives[0]
                    return f"{adjective} {translated}"
                return translated
                
        # 한국어 명사 영어 변환
        translated_nouns = []
        for noun in nouns:
            translated = self.korean_subject_map.get(noun, noun)
            translated_nouns.append(translated)
            
        # 주요 명사 찾기 - 우선순위 검사
        main_subject = None
        for subject in translated_nouns:
            if subject in ["child", "baby", "puppy", "kitten", "person", "woman", "man"]:
                main_subject = subject
                break
                
        if not main_subject and translated_nouns:
            main_subject = translated_nouns[0]
        elif not main_subject:
            main_subject = "scene"
        
        # 형용사와 결합 (중복 검사)
        if adjectives:
            adjective = adjectives[0]
            # 형용사가 이미 명사에 포함되어 있는지 확인
            if adjective not in main_subject:
                return f"{adjective} {main_subject}"
        
        return main_subject
    
    def _extract_action(self, verbs: List[str], text: str) -> str:
        """동작 추출 및 한국어-영어 매핑 강화"""
        # 특정 문구 감지를 통한 동작 결정
        if "노래를 부르" in text or "노래 부르" in text:
            return "singing"
        
        if "뛰노는" in text:
            return "playfully running"
        
        if not verbs:
            # 기본 동작들
            default_actions = {
                "moving": ["moving", "moving gracefully"],
                "playing": ["playfully moving", "playing"],
                "standing": ["standing", "standing majestically"]
            }
            
            # 텍스트에서 동작 관련 키워드 찾기
            for keyword, actions in default_actions.items():
                if keyword in text.lower():
                    return actions[0]
            
            return "appearing"
        
        # 첫 번째 동사 반환 (이미 영어로 변환됨)
        return verbs[0]
    
    def _extract_environment(self, text: str) -> str:
        """환경 추출 및 매핑 개선"""
        # 환경 설정 개선
        environment_map = {
            "밝은": "bright outdoor space",
            "어두운": "moody atmospheric setting",
            "실내": "cozy indoor environment",
            "실외": "open outdoor setting",
            "자연": "natural environment with greenery",
            "도시": "urban city environment",
            "숲": "lush forest setting",
            "해변": "sunny beach setting",
            "공원": "peaceful park setting",
            "집": "comfortable home setting",
            "산": "majestic mountain landscape",
            "바다": "peaceful ocean scene",
            "무대": "professional stage",
            "스튜디오": "professional studio"
        }
        
        # 노래 관련 환경 설정
        if "노래" in text or "부르" in text:
            specific_environments = ["무대", "스튜디오"]
            for env in specific_environments:
                if env in text:
                    return environment_map.get(env)
            return "professional stage setting"
        
        # 밝은 영상 키워드 확인
        if "밝은" in text and "영상" in text:
            return "bright setting"
        
        for keyword, env in environment_map.items():
            if keyword in text:
                return env
        
        return "natural setting"
    
    def _extract_style(self, adjectives: List[str], text: str) -> str:
        """스타일 추출 로직 개선"""
        style_mapping = {
            "귀여운": "cute",
            "밝은": "bright",
            "어두운": "dark",
            "화려한": "vibrant",
            "자연적인": "natural",
            "사실적인": "realistic",
            "예술적인": "artistic",
            "단순한": "minimalist"
        }
        
        # 형용사에서 스타일 추출
        extracted_styles = []
        for adj in adjectives:
            style = style_mapping.get(adj)
            if style:
                extracted_styles.append(style)
            else:
                # 이미 영어 형용사인 경우
                extracted_styles.append(adj)
        
        # 텍스트에서 직접 스타일 키워드 찾기
        style_keywords = {
            "시네마틱": "cinematic",
            "드라마틱": "dramatic",
            "미니멀": "minimalist",
            "다이나믹": "dynamic",
            "분위기있는": "atmospheric",
            "밝은": "bright"
        }
        
        for keyword, style in style_keywords.items():
            if keyword in text:
                extracted_styles.append(style)
        
        # 특정 환경 조건에 따른 스타일 설정
        if "밝은" in text:
            extracted_styles.append("bright")
        
        if "자연" in text:
            extracted_styles.append("natural")
        
        # 중복 스타일 필터링
        unique_styles = list(set(extracted_styles))
        
        # 스타일 우선순위 지정
        priority_order = ["cinematic", "bright", "vibrant", "natural", "artistic", "realistic", "cute"]
        sorted_styles = []
        
        for priority_style in priority_order:
            if priority_style in unique_styles:
                sorted_styles.append(priority_style)
        
        # 우선순위에 없는 스타일들 추가
        for style in unique_styles:
            if style not in sorted_styles:
                sorted_styles.append(style)
        
        # 최대 2개 스타일만 사용
        final_styles = sorted_styles[:2] if sorted_styles else ["natural"]
        
        return ", ".join(final_styles)
    
    def _determine_category(self, subject: str) -> PromptCategory:
        """카테고리 결정"""
        subject_lower = subject.lower()
        
        # 사람 관련 카테고리 확인 (특수 케이스)
        person_keywords = ["woman", "man", "person", "child", "baby", "portrait"]
        if any(keyword in subject_lower for keyword in person_keywords):
            return PromptCategory.PERSON
        
        # 일반 카테고리 매칭
        for category, template in self.templates.items():
            keywords = template.get("keywords", [])
            if any(keyword in subject_lower for keyword in keywords):
                return category
        
        return PromptCategory.GENERAL
    
    def _build_prompt(self, elements: ExtractedElements, template: Dict[str, str]) -> str:
        """최종 프롬프트 구성"""
        structure = template["structure"]
        
        # 템플릿 변수 매핑
        template_vars = {
            "adjective": elements.style.split(", ")[0] if ", " in elements.style else elements.style,
            "animal": elements.subject,
            "subject": elements.subject,
            "action": elements.action,
            "doing": elements.action,
            "environment": elements.environment,
            "scene_type": elements.subject,
            "style": elements.style,
            "description": f"{elements.subject} {elements.action}",
            "elements": "natural elements",
            "lighting": "natural",
            "quality": random.choice(self.quality_enhancers)
        }
        
        # 스타일이 이미 주제/형용사에 포함된 경우 중복 제거
        main_style = template_vars["style"]
        if main_style in template_vars["adjective"]:
            # 형용사가 이미 스타일을 포함하면 스타일을 natural로 변경
            template_vars["style"] = "natural"
        
        # 템플릿 적용
        try:
            prompt = structure.format(**template_vars)
        except KeyError:
            # 템플릿 변수가 없을 경우 기본 프롬프트 생성
            prompt = f"{elements.subject} {elements.action} in {elements.environment}, {elements.style}, high quality"
        
        # 중복 단어 및 스타일 제거
        prompt = self._remove_duplicate_words(prompt)
        
        return prompt.strip()
    
    def _remove_duplicate_words(self, text: str) -> str:
        """중복 단어 제거 - 향상된 버전"""
        # 1. 연속된 동일 단어 제거
        cleaned_text = re.sub(r'\b(\w+)(\s+\1\b)+', r'\1', text)
        
        # 2. 콤마로 분리된 중복 단어 찾아서 제거
        segments = cleaned_text.split(', ')
        unique_segments = []
        seen_words = set()
        
        for segment in segments:
            segment_words = set(re.findall(r'\b\w+\b', segment.lower()))
            # 이미 처리된 단어들과 중복 확인
            if not any(word in seen_words for word in segment_words):
                unique_segments.append(segment)
                seen_words.update(segment_words)
        
        # 3. 동사 중복 제거 - 한국어 원본과 영어 번역이 함께 있는 경우
        result = ', '.join(unique_segments)
        
        # 4. 최종 중복 확인 및 공백 정리
        result = re.sub(r'\s{2,}', ' ', result)
        result = re.sub(r',\s*,', ',', result)
        
        return result

# 사용 예시
if __name__ == "__main__":
    import asyncio
    
    async def test():
        generator = PromptGenerator()
        
        test_inputs = [
            "귀여운 강아지가 뛰노는 밝은 영상",
            "아름다운 숲 속의 자연 풍경",
            "사람이 해변을 걷는 모습",
            "아름다운 여성이 노래를 부르는 영상",
            "예쁜 아이가 뛰노는 밝은 영상"
        ]
        
        for input_text in test_inputs:
            result = await generator.generate_prompt(input_text)
            print(f"입력: {result['original_input']}")
            print(f"결과: {result['optimized_prompt']}")
            print(f"카테고리: {result['category']}")
            print("---")
    
    asyncio.run(test())