# 프롬프트 최적화 기반 영상 생성 에이전트 시스템

자연어 입력을 받아 영상 콘텐츠를 생성하고, 프롬프트 수정 이력을 Diff 형태로 로깅하는 AI 에이전트 시스템입니다.

## 주요 기능

1. **사용자 입력 인터페이스**
   - 사용자가 원하는 영상의 콘셉트/느낌 등을 자연어로 입력
   - 예: "귀여운 강아지가 뛰노는 밝은 영상"

2. **프롬프트 생성 및 편집**
   - 입력 기반으로 AI 영상 생성용 텍스트 프롬프트 자동 생성
   - 사용자가 프롬프트를 직접 수정 가능한 UI 제공
   - 수정 전/후의 Diff를 JSON 형태로 기록

3. **영상 생성**
   - 최종 프롬프트를 기반으로 10초 영상 생성
   - WebM 형식과 VP80 코덱 활용으로 Streamlit 호환성 보장

4. **프롬프트 이력 저장 및 재활용**
   - 수정된 프롬프트와 Diff를 MongoDB에 저장
   - 유사한 요청 시 최적화된 프롬프트 추천

5. **결과 확인 인터페이스**
   - 생성된 영상을 UI 상에서 확인 가능
   - 수정된 프롬프트 및 Diff 내용 시각적 표시

## 시스템 아키텍처

```mermaid
graph TD
    subgraph "프로덕션급 최적화 아키텍처"
    %% 핵심 컴포넌트
    UI[("🌐 사용자 인터페이스")]:::blue
    PG[("🤖 프롬프트 엔진")]:::green
    CM[("💾 캐싱 시스템")]:::cyan
    MM[("📊 모니터링 대시보드")]:::pink
    
    %% 확장 모듈
    subgraph Resilience["🛡️ 시스템 복원력"]
        EM[("⚠️ 에러 처리기")]
        RM[("🔄 재시도 관리자")]
        FM[("🆘 폴백 메커니즘")]
    end
    
    %% 데이터 흐름
    UI -->|요청| PG
    PG -->|캐시 조회| CM
    CM -->|히트| PG
    CM -->|미스| HM[("📚 이력 관리자")]
    PG -->|비동기 처리| VG[("🎬 영상 생성기")]
    VG -->|결과| UI
    VG -->|로그| MM
    EM -->|장애 전파| MM
    RM -->|API 재시도| VG
    FM -->|대체 콘텐츠| UI
    end
    
    classDef blue fill:#93c5fd,stroke:#1e3a8a
    classDef green fill:#6ee7b7,stroke:#065f46
    classDef cyan fill:#67e8f9,stroke:#0e7490
    classDef pink fill:#f9a8d4,stroke:#9d174d
핵심 컴포넌트

사용자 인터페이스(UI)

Streamlit 웹 애플리케이션을 통한 직관적인 사용자 경험
콘셉트 입력, 프롬프트 편집, 결과 확인을 위한 통합 인터페이스


프롬프트 생성기(PromptGenerator)

자연어 입력을 분석하여 AI 비디오 생성에 최적화된 프롬프트 생성
한국어-영어 변환 및 스타일 우선순위 적용
콘텐츠 카테고리 자동 분류 및 템플릿 기반 프롬프트 구성


프롬프트 편집기(PromptEditor)

원본 프롬프트와 편집된 프롬프트 간의 차이 분석
JSON 형식의 Diff 생성 및 시각화


영상 생성기(VideoGenerator)

최종 프롬프트 기반 영상 생성(WebM 형식, VP80 코덱)
키워드 기반 색상 및 움직임 스타일 결정
프로그레스 바 및 캡션 자동 생성


이력 관리자(HistoryManager)

MongoDB를 통한 프롬프트 이력 저장
유사 프롬프트 검색 및 추천 기능


캐시 관리자(CacheManager)

Redis를 사용한 결과 캐싱
반복 요청 처리 최적화



데이터 흐름 및 워크플로우
mermaidsequenceDiagram
    participant User as 🧑💻 사용자
    participant UI as 🖥️ UI
    participant PG as 🤖 프롬프트 엔진
    participant CM as 💾 캐싱 시스템
    participant HM as 📚 이력 관리자
    participant VG as 🎬 영상 생성기
    participant EM as ⚠️ 에러 처리기
    
    User->>UI: 자연어 요청 ("눈 내리는 산타마을")
    UI->>PG: 처리 요청
    PG->>CM: 캐시 조회 (유사도 90% 이상)
    alt 캐시 히트
        CM-->>PG: 최적화된 프롬프트 반환
    else 캐시 미스
        PG->>HM: 벡터 DB 검색
        HM-->>PG: 유사 이력 3건
        PG->>PG: 조합 최적화 수행
    end
    PG->>VG: 프롬프트 전송 (비동기)
    par 병렬 처리
        VG->>VG: 영상 렌더링 (GPU 가속)
        VG->>MM: 메트릭 기록 (FPS, Latency)
    end
    alt 성공
        VG-->>UI: 영상 URL 전송
    else 타임아웃
        VG->>EM: 에러 코드 504
        EM->>RM: 3회 재시도
        RM->>VG: 재처리 요청
        alt 복구 성공
            VG-->>UI: 지연 결과 전송
        else 실패
            EM->>FM: 대체 영상 활성화
            FM-->>UI: 기본 애니메이션 제공
        end
    end
    UI->>User: 최종 결과 표시
설치 및 실행 방법
환경 요구사항

Docker 및 Docker Compose 설치
최소 2GB RAM 및 10GB 저장 공간
인터넷 연결

설치 및 실행 단계

저장소 복제

bashgit clone https://github.com/JO-HEEJIN/video-generation-agent.git
cd video-generation-agent

환경 설정

bashcp .env.example .env

Docker 컨테이너 실행

bashdocker-compose build
docker-compose up -d

웹 인터페이스 접속

http://localhost:8501
사용 예시
자연어 입력 → 프롬프트 생성

웹 인터페이스 상단의 텍스트 영역에 "귀여운 강아지가 뛰노는 밝은 영상"을 입력합니다.
"프롬프트 생성" 버튼을 클릭합니다.
시스템이 처리한 후 "생성된 프롬프트" 섹션에 영어로 변환된 최적화 프롬프트가 표시됩니다.

예시 결과:
cute puppy playfully running in well-lit outdoor space, bright, vibrant style, 4K resolution
프롬프트 편집 및 Diff 생성

생성된 프롬프트 텍스트 영역에서 내용을 수정합니다.
수정 후 자동으로 Diff가 생성되어 "변경 사항 분석" 섹션에 JSON 형태로 표시됩니다.

영상 생성 및 결과 확인

"영상 생성 설정" 섹션에서 영상 길이를 선택합니다.
"영상 생성 시작" 버튼을 클릭합니다.
생성된 영상이 "생성 결과" 섹션에 표시됩니다.

기술 스택

프론트엔드: Streamlit
백엔드: Python 3.10
데이터베이스: MongoDB, Redis
비디오 처리: OpenCV (cv2)
컨테이너화: Docker, Docker Compose
자연어 처리: 커스텀 NLP 파서

파일 구조
video-generation-agent/
├── data/                  # 데이터 저장소
│   ├── cache/             # 캐시 파일
│   ├── history/           # 로컬 히스토리 백업
│   └── videos/            # 생성된 비디오
├── docker/                # Docker 관련 파일
├── logs/                  # 로그 파일
├── monitoring/            # 모니터링 설정
├── tests/                 # 테스트 코드
│   ├── integration/       # 통합 테스트
│   └── unit/              # 단위 테스트
├── src/                   # 소스 코드
│   ├── components/        # 핵심 컴포넌트
│   │   ├── cache/         # 캐시 관리
│   │   ├── history/       # 이력 관리
│   │   ├── prompt_editor/ # 프롬프트 편집
│   │   ├── prompt_generator/ # 프롬프트 생성
│   │   └── video_generator/ # 영상 생성
│   ├── config/            # 설정 파일
│   ├── monitoring/        # 모니터링 코드
│   ├── utils/             # 유틸리티 함수
│   └── main.py            # 메인 애플리케이션
├── .env                   # 환경 변수
├── docker-compose.yml     # Docker Compose 설정
├── Dockerfile             # Docker 빌드 설정
└── requirements.txt       # Python 의존성
확장성 및 미래 계획

실제 AI 영상 생성 API 통합 (D-ID, Runway, Pika 등)
더 정교한 한국어 자연어 처리 구현
사용자 피드백 기반 프롬프트 최적화 학습
고해상도 영상 지원 및 다양한 비디오 형식 제공
