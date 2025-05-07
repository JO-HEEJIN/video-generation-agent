# src/components/video_generator/generator.py
import asyncio
import numpy as np
import cv2
import os
import base64
import io
import structlog
import random
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from typing import Dict, Any, List, Tuple, Optional
from pathlib import Path
from config.settings import settings

logger = structlog.get_logger()

class VideoGenerator:
   """최적화된 Mock 영상 생성기"""
   
   def __init__(self):
       self.output_dir = Path(settings.DATA_DIR) / "videos"
       self.output_dir.mkdir(exist_ok=True, parents=True)
       
       # 기본 설정
       self.default_resolution = (640, 360)  # 16:9 비율
       self.default_fps = 24
       self.default_duration = 5  # 초
   
   async def generate(self, prompt: str, duration: int = None, 
                      resolution: Tuple[int, int] = None) -> Dict[str, Any]:
       """개선된 비동기 영상 생성 메소드"""
       logger.info("video_generation_start", 
                   prompt=prompt[:30] + "..." if len(prompt) > 30 else prompt)
       
       duration = duration or self.default_duration
       resolution = resolution or self.default_resolution
       
       try:
           keywords = self._extract_keywords(prompt)
           video_id = f"video_{int(time.time())}_{random.randint(1000, 9999)}"
           
           # WebM 확장자 사용 - Streamlit 호환성 향상
           video_path = self.output_dir / f"{video_id}.webm"
           thumbnail_path = self.output_dir / f"{video_id}_thumb.jpg"
           
           # 동기 함수를 비동기로 실행
           await asyncio.to_thread(
               self._generate_mock_video,
               video_path,
               duration,
               resolution,
               self.default_fps,
               prompt,
               keywords
           )
           
           self._generate_thumbnail(video_path, thumbnail_path)
           
           return {
               "video_id": video_id,
               "video_url": str(video_path),  # 전체 경로 사용
               "thumbnail_url": str(thumbnail_path),
               "prompt": prompt,
               "keywords": keywords,
               "duration": duration,
               "resolution": f"{resolution[0]}x{resolution[1]}",
               "created_at": datetime.now().isoformat(),
               "success": True,
               "message": "영상이 성공적으로 생성되었습니다",
               "is_mock": True
           }
           
       except Exception as e:
           logger.error("video_generation_failed", error=str(e))
           return {
               "video_id": None,
               "video_url": None,
               "thumbnail_url": None,
               "success": False,
               "message": f"영상 생성 중 오류가 발생했습니다: {str(e)}",
               "is_mock": True
           }
   
   def _extract_keywords(self, prompt: str) -> List[str]:
       """프롬프트에서 키워드 추출"""
       words = prompt.lower().split()
       
       # 중요 키워드
       important_words = [
           "bright", "dark", "vibrant", "colorful", "monochrome",
           "cinematic", "dramatic", "peaceful", "action", "slow",
           "nature", "urban", "indoor", "outdoor", "portrait"
       ]
       
       # 한국어 키워드와 영어 매핑
       korean_mappings = {
           "밝은": "bright",
           "어두운": "dark",
           "화려한": "colorful",
           "자연": "nature",
           "실내": "indoor",
           "실외": "outdoor",
           "느린": "slow",
           "빠른": "fast"
       }
       
       # 추출된 키워드
       keywords = []
       
       # 영어 키워드 추출
       for word in words:
           if word in important_words:
               keywords.append(word)
       
       # 한국어 키워드 매핑
       for k_word, e_word in korean_mappings.items():
           if k_word in prompt:
               keywords.append(e_word)
       
       # 키워드가 없으면 기본값 추가
       if not keywords:
           keywords = ["standard", "video"]
       
       return keywords

   def _generate_mock_video(self, output_path: Path, duration: int, 
                           resolution: Tuple[int, int], fps: int, 
                           prompt: str, keywords: List[str]) -> None:
       """개선된 동기 영상 생성 메소드"""
       width, height = resolution
       color_scheme = self._determine_color_scheme(keywords)
       movement_style = self._determine_movement_style(keywords)
       
       # VP80 코덱 사용 - WebM 형식에 적합하며 Streamlit과 호환성 좋음
       # 참고: https://forum.opencv.org/t/opencv-video-streamlit/20100
       fourcc = cv2.VideoWriter_fourcc(*'VP80')
       out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
       
       try:
           total_frames = duration * fps
           for frame_idx in range(total_frames):
               frame = self._create_frame(
                   frame_idx, 
                   total_frames,
                   width, 
                   height,
                   prompt, 
                   color_scheme,
                   movement_style
               )
               out.write(frame)
       finally:
           out.release()
   
   def _create_frame(self, frame_idx: int, total_frames: int, 
                     width: int, height: int, prompt: str, 
                     color_scheme: List[Tuple[int, int, int]],
                     movement_style: str) -> np.ndarray:
       """단일 프레임 생성"""
       # 빈 프레임 생성
       frame = np.zeros((height, width, 3), dtype=np.uint8)
       
       # 진행률
       progress = frame_idx / total_frames
       
       # 움직임 스타일에 따른 처리
       if movement_style == "gradient":
           # 그라데이션 배경
           color1 = color_scheme[0]
           color2 = color_scheme[1]
           
           # 그라데이션 애니메이션
           shift = int(progress * 100) % 2
           if shift == 0:
               for y in range(height):
                   color_ratio = y / height
                   color = tuple(int(c1 * (1 - color_ratio) + c2 * color_ratio) 
                               for c1, c2 in zip(color1, color2))
                   frame[y, :] = color
           else:
               for x in range(width):
                   color_ratio = x / width
                   color = tuple(int(c1 * (1 - color_ratio) + c2 * color_ratio) 
                               for c1, c2 in zip(color1, color2))
                   frame[:, x] = color
                   
       elif movement_style == "particles":
           # 파티클 애니메이션
           frame.fill(50)  # 어두운 배경
           
           # 파티클 수
           num_particles = 50
           
           for i in range(num_particles):
               # 파티클 위치
               x = int(width * (0.2 + 0.6 * ((i * 7 + frame_idx) % 100) / 100))
               y = int(height * (0.2 + 0.6 * ((i * 13 + frame_idx) % 100) / 100))
               
               # 파티클 크기 (최소값 1 보장)
               size = max(1, int(5 + 10 * np.sin(frame_idx / 20 + i)))
               
               # 파티클 색상
               color = color_scheme[i % len(color_scheme)]
               
               # 파티클 그리기
               cv2.circle(frame, (x, y), size, color, -1)
               
       elif movement_style == "wave":
           # 웨이브 애니메이션
           frame.fill(20)  # 어두운 배경
           
           # 웨이브 파라미터
           amplitude = height / 10
           frequency = 2 * np.pi / width * 3
           phase = 2 * np.pi * progress * 2
           
           # 색상 인덱스
           color_idx = int(progress * len(color_scheme)) % len(color_scheme)
           color = color_scheme[color_idx]
           
           # 웨이브 그리기
           for x in range(width):
               # 여러 웨이브 합성
               y1 = int(height/2 + amplitude * np.sin(frequency * x + phase))
               y2 = int(height/2 + amplitude * np.sin(frequency * x + phase + np.pi))
               y3 = int(height/2 + amplitude/2 * np.sin(frequency*2 * x + phase*1.5))
               
               # 선으로 연결
               cv2.line(frame, (x, y1), (x, y1-5), color, 2)
               cv2.line(frame, (x, y2), (x, y2-5), (color[0]//2, color[1]//2, color[2]//2), 2)
               cv2.line(frame, (x, y3), (x, y3-5), (color[0]//3, color[1]//3, color[2]//3), 2)
       
       else:  # 기본 애니메이션
           # 단순 컬러 변환
           color_idx = int(progress * len(color_scheme)) % len(color_scheme)
           frame[:] = color_scheme[color_idx]
       
       # 텍스트 추가
       self._add_text_to_frame(frame, prompt, progress)
       
       return frame
   
   def _add_text_to_frame(self, frame: np.ndarray, prompt: str, progress: float) -> None:
       """프레임에 텍스트 추가"""
       height, width = frame.shape[:2]
       
       # 기본 설정
       font = cv2.FONT_HERSHEY_SIMPLEX
       font_scale = 0.7
       thickness = 2
       color = (255, 255, 255)
       
       # 프롬프트 줄바꿈
       max_chars = width // 15  # 글자당 평균 픽셀 수
       prompt_lines = self._wrap_text(prompt, max_chars)
       
       # 텍스트 위치
       y_position = height - 10 - len(prompt_lines) * 30
       
       # "AI 생성 영상" 텍스트
       cv2.putText(frame, "AI Generated Video", (20, 40), 
                  font, 1.0, (255, 255, 255), thickness+1)
       
       # 프로그레스 바
       bar_width = int(width * 0.8)
       bar_height = 10
       bar_x = int((width - bar_width) / 2)
       bar_y = height - 30
       
       # 배경 바
       cv2.rectangle(frame, (bar_x, bar_y), (bar_x + bar_width, bar_y + bar_height), 
                    (100, 100, 100), -1)
       
       # 진행 바
       filled_width = int(bar_width * progress)
       cv2.rectangle(frame, (bar_x, bar_y), (bar_x + filled_width, bar_y + bar_height), 
                    (0, 255, 255), -1)
       
       # 프롬프트 표시
       for i, line in enumerate(prompt_lines):
           y = y_position + i * 30
           cv2.putText(frame, line, (20, y), font, font_scale, color, thickness)
   
   def _wrap_text(self, text: str, max_length: int) -> List[str]:
       """텍스트 줄바꿈"""
       words = text.split()
       lines = []
       current_line = []
       current_length = 0
       
       for word in words:
           if current_length + len(word) + 1 <= max_length:
               current_line.append(word)
               current_length += len(word) + 1
           else:
               lines.append(" ".join(current_line))
               current_line = [word]
               current_length = len(word)
       
       if current_line:
           lines.append(" ".join(current_line))
       
       # 최대 3줄로 제한
       if len(lines) > 3:
           lines = lines[:2]
           lines.append(lines[2] + "...")
       
       return lines
   
   def _determine_color_scheme(self, keywords: List[str]) -> List[Tuple[int, int, int]]:
       """키워드 기반 색상 스키마 결정"""
       # 기본 색상 스키마
       default_scheme = [(100, 100, 100), (150, 150, 150)]
       
       # 미리 정의된 색상 스키마
       color_schemes = {
           "bright": [(200, 200, 100), (100, 200, 200), (200, 100, 200)],
           "dark": [(50, 30, 80), (80, 30, 50), (30, 50, 80)],
           "colorful": [(255, 50, 50), (50, 255, 50), (50, 50, 255), (255, 255, 50)],
           "nature": [(50, 150, 50), (100, 200, 100), (150, 100, 50)],
           "urban": [(100, 100, 120), (120, 100, 100), (70, 90, 100)],
           "cinematic": [(20, 60, 100), (100, 60, 20), (60, 20, 100)]
       }
       
       # 키워드 매칭
       for keyword in keywords:
           if keyword in color_schemes:
               return color_schemes[keyword]
       
       return default_scheme
   
   def _determine_movement_style(self, keywords: List[str]) -> str:
       """키워드 기반 움직임 스타일 결정"""
       style_mappings = {
           "slow": "gradient",
           "fast": "particles",
           "dynamic": "wave",
           "vibrant": "particles",
           "calm": "gradient",
           "peaceful": "gradient",
           "action": "wave"
       }
       
       for keyword in keywords:
           if keyword in style_mappings:
               return style_mappings[keyword]
       
       # 랜덤 선택
       return random.choice(["gradient", "particles", "wave"])
   
   def _generate_thumbnail(self, video_path: Path, thumbnail_path: Path) -> None:
       """영상에서 썸네일 추출"""
       try:
           cap = cv2.VideoCapture(str(video_path))
           
           if not cap.isOpened():
               raise Exception("영상 파일을 열 수 없습니다")
           
           # 프레임 읽기 (첫 프레임 사용)
           ret, frame = cap.read()
           if not ret:
               raise Exception("프레임을 읽을 수 없습니다")
           
           # 썸네일 저장
           cv2.imwrite(str(thumbnail_path), frame)
           
           # 자원 정리
           cap.release()
           
       except Exception as e:
           logger.error("thumbnail_generation_failed", error=str(e))
           # 기본 썸네일 생성
           self._create_default_thumbnail(thumbnail_path)
   
   def _create_default_thumbnail(self, thumbnail_path: Path) -> None:
       """기본 썸네일 생성"""
       width, height = 640, 360  # 16:9 비율
       
       # 빈 이미지 생성
       img = np.zeros((height, width, 3), dtype=np.uint8)
       img.fill(80)  # 회색 배경
       
       # 텍스트 추가
       font = cv2.FONT_HERSHEY_SIMPLEX
       cv2.putText(img, "Video Thumbnail", (width//4, height//2), 
                  font, 1.5, (255, 255, 255), 2)
       
       # 저장
       cv2.imwrite(str(thumbnail_path), img)

# 사용 예시
if __name__ == "__main__":
   async def test():
       generator = VideoGenerator()
       result = await generator.generate("밝은 자연 풍경의 아름다운 숲")
       print(f"비디오 생성 결과: {result}")
   
   asyncio.run(test())