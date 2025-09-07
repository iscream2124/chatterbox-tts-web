#!/bin/bash

echo "🎤 Chatterbox TTS 로컬 실행 스크립트"
echo "=================================="

# Python 가상환경 확인
if [ ! -d "venv" ]; then
    echo "📦 Python 가상환경 생성 중..."
    python3 -m venv venv
fi

# 가상환경 활성화
echo "🔧 가상환경 활성화 중..."
source venv/bin/activate

# pip 업그레이드
echo "⬆️ pip 업그레이드 중..."
pip install --upgrade pip

# setuptools 다운그레이드 (Python 3.13 호환성)
echo "🔧 setuptools 다운그레이드 중..."
pip install "setuptools<70.0"

# chatterbox 모듈 설치
echo "📥 chatterbox 모듈 설치 중..."
pip install git+https://github.com/resemble-ai/chatterbox.git

# Streamlit 실행
echo "🚀 Streamlit 앱 실행 중..."
echo "🌐 브라우저에서 http://localhost:8501 접속하세요"
streamlit run streamlit_app.py
