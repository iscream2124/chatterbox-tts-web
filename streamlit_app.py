import streamlit as st
import os
import uuid
import torch
import torchaudio as ta
from chatterbox.mtl_tts import ChatterboxMultilingualTTS, SUPPORTED_LANGUAGES

# 페이지 설정
st.set_page_config(
    page_title="Chatterbox TTS - 한국어 음성 합성",
    page_icon="🎤",
    layout="wide"
)

# 제목
st.title("🎤 Chatterbox TTS - 한국어 음성 합성")
st.markdown("---")

# TTS 모델 로드
@st.cache_resource
def load_model():
    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"
    
    st.info(f"사용 중인 디바이스: {device}")
    
    # torch.load 패치 (Mac M1/M2/M3/M4용)
    map_location = torch.device(device)
    torch_load_original = torch.load
    def patched_torch_load(*args, **kwargs):
        if 'map_location' not in kwargs:
            kwargs['map_location'] = map_location
        return torch_load_original(*args, **kwargs)
    torch.load = patched_torch_load
    
    with st.spinner("다국어 TTS 모델을 로드하는 중..."):
        model = ChatterboxMultilingualTTS.from_pretrained(device=device)
    st.success("다국어 TTS 모델 로드 완료!")
    return model

# 모델 로드
model = load_model()

# 사이드바 설정
st.sidebar.header("🎛️ 음성 설정")

# 텍스트 입력
text = st.text_area(
    "📝 변환할 텍스트를 입력하세요:",
    value="안녕하세요! 저는 Chatterbox TTS입니다. 한국어 음성 합성을 테스트하고 있습니다.",
    height=100
)

# 언어 선택
language = st.sidebar.selectbox(
    "🌍 언어 선택:",
    options=["ko", "en", "ja", "zh"],
    format_func=lambda x: {"ko": "한국어", "en": "영어", "ja": "일본어", "zh": "중국어"}[x],
    index=0
)

# 감정 선택 (참고용 - 실제로는 사용되지 않음)
st.sidebar.info("ℹ️ ChatterboxMultilingualTTS는 감정 파라미터를 직접 지원하지 않습니다. 음성 파라미터로 조절하세요.")

# 음성 파라미터
st.sidebar.subheader("🎚️ 음성 파라미터")

speed = st.sidebar.slider(
    "속도",
    min_value=0.5,
    max_value=2.0,
    value=1.0,
    step=0.1
)

exaggeration = st.sidebar.slider(
    "감정 강도",
    min_value=0.5,
    max_value=2.0,
    value=1.0,
    step=0.1
)

cfg_weight = st.sidebar.slider(
    "CFG 가중치",
    min_value=0.0,
    max_value=1.0,
    value=0.5,
    step=0.1
)

# TTS 생성 버튼
if st.button("🎵 음성 생성", type="primary"):
    if not text.strip():
        st.error("텍스트를 입력해주세요!")
    else:
        with st.spinner("음성을 생성하는 중..."):
            try:
                # TTS 생성 (기본 파라미터만 사용)
                wav = model.generate(
                    text,
                    language_id=language
                )
                
                # 오디오 파일 저장
                filename = f"tts_{uuid.uuid4().hex[:8]}.wav"
                filepath = f"/tmp/{filename}"
                ta.save(filepath, wav, model.sr)
                
                # 오디오 재생
                with open(filepath, "rb") as audio_file:
                    audio_bytes = audio_file.read()
                
                st.audio(audio_bytes, format="audio/wav")
                
                # 다운로드 버튼
                st.download_button(
                    label="💾 오디오 다운로드",
                    data=audio_bytes,
                    file_name=filename,
                    mime="audio/wav"
                )
                
                st.success("음성 생성 완료!")
                
            except Exception as e:
                st.error(f"음성 생성 중 오류가 발생했습니다: {str(e)}")

# 정보 섹션
st.markdown("---")
st.subheader("ℹ️ 사용법")
st.markdown("""
1. **텍스트 입력**: 변환하고 싶은 텍스트를 입력하세요
2. **언어 선택**: 한국어, 영어, 일본어, 중국어 중 선택
3. **음성 파라미터 조절**: 속도, 감정 강도, CFG 가중치 조절
4. **음성 생성**: 버튼을 클릭하여 음성을 생성하세요
""")

st.subheader("🎯 지원 기능")
st.markdown("""
- ✅ **23개 언어 지원** (한국어, 영어, 일본어, 중국어 등)
- ✅ **음성 파라미터 조절** (속도, 감정 강도, CFG 가중치)
- ✅ **고품질 음성 합성** (자연스러운 억양과 발음)
- ✅ **실시간 오디오 재생** 및 다운로드
""")

# 푸터
st.markdown("---")
st.markdown("**Chatterbox TTS** - 고품질 음성 합성 서비스")
