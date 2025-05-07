# src/main.py
import streamlit as st
import asyncio
import os
from datetime import datetime
from pathlib import Path
from config.settings import settings
from config.logging import setup_logging
from components.prompt_generator.generator import PromptGenerator
from components.prompt_editor.editor import PromptEditor
from components.video_generator.generator import VideoGenerator
from components.history.history_manager import HistoryManager
from components.cache.cache_manager import CacheManager

logger = setup_logging()

def main():
    st.set_page_config(
        page_title=settings.APP_NAME,
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🎬 프롬프트 최적화 영상 생성 에이전트")
    
    # 컴포넌트 초기화
    prompt_generator = PromptGenerator()
    prompt_editor = PromptEditor()
    video_generator = VideoGenerator()
    history_manager = HistoryManager()
    cache_manager = CacheManager()
    
    # 세션 상태 초기화
    session_defaults = {
        'current_prompt': "",
        'original_prompt': "",
        'diff_result': None,
        'request_history': [],
        'video_result': None,
        'similar_prompts': []
    }
    for key, val in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val
    
    # 메인 레이아웃
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 사용자 입력 섹션
        st.header("💡 영상 콘셉트 입력")
        user_input = st.text_area(
            "원하는 영상의 콘셉트를 자연어로 입력하세요",
            height=100,
            placeholder="예: 귀여운 강아지가 뛰노는 밝은 영상",
            key="user_input"
        )
        
        # 프롬프트 생성 제어
        col1_1, col1_2 = st.columns([1, 4])
        with col1_1:
            generate_btn = st.button("프롬프트 생성", type="primary")
        with col1_2:
            auto_optimize = st.checkbox("자동 최적화 적용", value=True, key="auto_optimize")
        
        # 유사 프롬프트 제안
        if user_input and len(user_input) > 10:
            st.session_state.similar_prompts = history_manager.find_similar_prompts(user_input)
            if st.session_state.similar_prompts:
                with st.expander("🚀 유사한 이전 프롬프트 추천", expanded=True):
                    for idx, prompt in enumerate(st.session_state.similar_prompts[:3]):
                        st.markdown(f"**추천 {idx+1}**")
                        st.caption(f"입력: {prompt['input']}")
                        # 수정된 부분: prompt 키 대신 다양한 키 확인
                        if 'edited_prompt' in prompt:
                            st.code(prompt['edited_prompt'], language="text")
                        elif 'original_prompt' in prompt:
                            st.code(prompt['original_prompt'], language="text")
                        else:
                            st.code("프롬프트를 찾을 수 없음", language="text")
                        if st.button(f"이 프롬프트 사용하기 #{idx+1}"):
                            # 수정된 부분: 적절한 키 사용
                            prompt_key = next((k for k in ['edited_prompt', 'original_prompt'] if k in prompt), None)
                            if prompt_key:
                                st.session_state.current_prompt = prompt[prompt_key]
                                st.session_state.original_prompt = prompt[prompt_key]
                                st.rerun()
        
        # 프롬프트 생성 처리
        if generate_btn and user_input:
            with st.spinner("프롬프트 생성 중..."):
                try:
                    cached = cache_manager.get(f"prompt:{user_input}")
                    if cached:
                        result = cached
                        st.toast("캐시된 결과를 불러왔습니다", icon="💾")
                    else:
                        result = asyncio.run(prompt_generator.generate_prompt(user_input))
                        cache_manager.set(f"prompt:{user_input}", result)
                    
                    st.session_state.original_prompt = result['optimized_prompt']
                    st.session_state.current_prompt = result['optimized_prompt']
                    st.session_state.diff_result = None
                    st.session_state.video_result = None
                except Exception as e:
                    st.error(f"오류 발생: {str(e)}")
                    logger.error("Prompt generation error", error=str(e))
        
        # 프롬프트 편집 및 분석
        if st.session_state.current_prompt:
            st.subheader("✨ 생성된 프롬프트")
            new_prompt = st.text_area(
                "프롬프트 (편집 가능)",
                value=st.session_state.current_prompt,
                height=150,
                key="prompt_editor"
            )
            
            # 변경 사항 감지
            if new_prompt != st.session_state.current_prompt:
                st.session_state.current_prompt = new_prompt
                st.session_state.diff_result = prompt_editor.generate_diff(
                    st.session_state.original_prompt,
                    st.session_state.current_prompt
                )
                history_manager.save_history({
                    'input': user_input,
                    'original_prompt': st.session_state.original_prompt,
                    'edited_prompt': new_prompt,
                    'diff': st.session_state.diff_result
                })
            
            # Diff 분석 표시
            if st.session_state.diff_result:
                with st.expander("📝 변경 사항 분석", expanded=True):
                    st.json(st.session_state.diff_result, expanded=False)
            
            # 영상 생성 섹션
            st.subheader("🎥 영상 생성 설정")
            duration = st.slider("영상 길이 (초)", 5, 15, 10)
            if st.button("영상 생성 시작", type="secondary", key="video_gen"):
                with st.spinner("영상 생성 중... 약 10-20초 소요됩니다"):
                    try:
                        video_result = asyncio.run(
                            video_generator.generate(
                                st.session_state.current_prompt,
                                duration=duration
                            )
                        )
                        st.session_state.video_result = video_result
                        st.toast("영상 생성 완료!", icon="✅")
                    except Exception as e:
                        st.error(f"영상 생성 실패: {str(e)}")
                        logger.error("Video generation error", error=str(e))
            
            # 영상 결과 표시
            if st.session_state.video_result:
                st.subheader("🎬 생성 결과")
                if st.session_state.video_result['success']:
                    video_path = Path(settings.DATA_DIR) / st.session_state.video_result['video_url']
                    
                    tab1, tab2 = st.tabs(["미리보기", "상세 정보"])
                    with tab1:
                        if video_path.exists():
                            st.video(str(video_path))
                        else:
                            st.error("비디오 파일을 찾을 수 없습니다")
                    with tab2:
                        st.json(st.session_state.video_result, expanded=False)
                else:
                    st.error("영상 생성 실패: " + st.session_state.video_result.get('message', '알 수 없는 오류'))

    with col2:
        # 히스토리 패널
        st.header("📚 작업 히스토리")
        history = history_manager.get_recent_history(limit=5)
        if history:
            for idx, entry in enumerate(history):
                with st.expander(f"작업 {idx+1} - {entry.get('input','')[:20]}", expanded=False):
                    st.markdown(f"**입력:** {entry['input']}")
                    st.markdown(f"**원본 프롬프트:**")
                    st.code(entry['original_prompt'], language="text")
                    st.markdown(f"**수정 프롬프트:**")
                    st.code(entry['edited_prompt'], language="text")
                    st.markdown("**변경 사항:**")
                    st.json(entry['diff'], expanded=False)
                    st.caption(f"생성 시간: {entry['timestamp']}")
        else:
            st.info("아직 저장된 히스토리가 없습니다")
        
        # 시스템 모니터링
        st.header("⚙️ 시스템 상태")
        st.metric("서버 상태", "정상 작동" if settings.APP_ENV == "production" else "개발 모드")
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            st.metric("Redis", "연결됨" if cache_manager.redis is not None else "연결 안 됨")
        with col2_2:
            # 수정된 부분: collection 비교 방식 변경
            st.metric("MongoDB", "연결됨" if history_manager.collection is not None else "연결 안 됨")
        
        # 도움말 섹션
        with st.expander("❓ 사용 가이드", expanded=False):
            st.markdown("""
            ### 사용 방법
            1. 영상 콘셉트를 자연어로 입력 (예: "화려한 불꽃놀이 장면")
            2. "프롬프트 생성" 버튼 클릭
            3. 생성된 프롬프트를 필요에 따라 수정
            4. "영상 생성" 버튼으로 최종 결과물 생성
            
            ### 고급 기능
            - 자동 최적화: 프롬프트 생성 시 AI가 자동으로 최적화 수행
            - 히스토리: 이전 작업 결과를 언제든지 확인하고 재사용 가능
            - 유사 프롬프트 추천: 비슷한 콘셉트의 이전 작업을 자동 추천
            """)

if __name__ == "__main__":
    main()