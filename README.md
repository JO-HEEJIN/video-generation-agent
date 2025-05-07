# 프롬프트 최적화 기반 영상 생성 에이전트 시스템

자연어 입력을 받아 영상 콘텐츠를 생성하고, 프롬프트 수정 이력을 Diff 형태로 로깅하는 AI 에이전트 시스템입니다.

## 프로젝트 개요

이 프로젝트는 사용자가 자연어로 입력한 영상 콘셉트를 분석하여 AI 영상 생성에 최적화된 프롬프트로 변환하고, 영상을 생성하는 과정을 자동화합니다. 사용자 편집 기능과 이력 관리를 통해 프롬프트 최적화 과정을 지속적으로 개선할 수 있습니다.

## 주요 기능

1. **사용자 입력 인터페이스**
   - 사용자가 원하는 영상의 콘셉트를 자연어로 입력
   - 예: "귀여운 강아지가 뛰노는 밝은 영상"

2. **프롬프트 생성 및 편집**
   - 입력 기반으로 AI 영상 생성용 텍스트 프롬프트 자동 생성
   - 한국어 입력을 영어 프롬프트로 자연스럽게 변환
   - 사용자가 프롬프트를 직접 수정 가능한 UI 제공
   - 수정 전/후의 Diff를 JSON 형태로 기록

3. **영상 생성**
   - 최종 프롬프트를 기반으로 VP80 코덱과 WebM 형식의 영상 생성
   - 프롬프트 키워드에 따른 색상 스키마 및 움직임 패턴 적용

4. **프롬프트 이력 저장 및 재활용**
   - MongoDB를 통한 프롬프트 이력 저장
   - Redis를 활용한 캐싱으로 유사 요청 처리 최적화
   - 유사한 요청 시 최적화된 프롬프트 추천

5. **결과 확인 인터페이스**
   - 생성된 영상을 Streamlit UI에서 직접 확인
   - 수정된 프롬프트 및 Diff 내용 시각적 표시

## 설치 및 실행 방법

### 요구사항
- Docker 및 Docker Compose
- 최소 2GB RAM
- 인터넷 연결

### 설치 및 실행
```bash
# 저장소 복제
git clone https://github.com/JO-HEEJIN/video-generation-agent.git
cd video-generation-agent

# 환경 설정
cp .env.example .env

# Docker 실행
docker-compose build
docker-compose up -d

# 웹 인터페이스 접속
# http://localhost:8501
기술 스택

프론트엔드: Streamlit
백엔드: Python 3.10
데이터베이스: MongoDB, Redis
비디오 처리: OpenCV (cv2)
컨테이너화: Docker, Docker Compose

프로젝트 구조
주요 코드는 video-generation-agent 디렉토리 내에 있습니다:
video-generation-agent/
├── src/
│   ├── components/          # 핵심 컴포넌트
│   │   ├── cache/          # 캐시 관리
│   │   ├── history/        # 이력 관리
│   │   ├── prompt_editor/  # 프롬프트 편집
│   │   ├── prompt_generator/ # 프롬프트 생성
│   │   └── video_generator/ # 영상 생성
│   ├── config/             # 설정 파일
│   └── main.py             # 메인 애플리케이션
├── data/                   # 데이터 저장소
├── docker-compose.yml      # Docker 설정
└── requirements.txt        # 의존성 패키지
라이선스
MIT License
