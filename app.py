#!/usr/bin/env python3
"""
Chatterbox TTS 웹 서비스
온라인에서 사용할 수 있는 TTS 웹 애플리케이션
"""

import os
import sys
import json
import torch
import torchaudio as ta
from flask import Flask, request, jsonify, render_template, send_file, session
from flask_cors import CORS
import threading
import time
from datetime import datetime
import uuid
import hashlib

# Chatterbox TTS 모듈 import
try:
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    print("✅ Chatterbox TTS 모듈 로드 성공")
except ImportError as e:
    print(f"❌ Chatterbox TTS 모듈 로드 실패: {e}")
    sys.exit(1)

app = Flask(__name__)
app.secret_key = 'chatterbox-tts-secret-key-2024'
CORS(app)

class TTSWebService:
    def __init__(self):
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "mps" if torch.backends.mps.is_available() else "cpu"
        self.is_loading = False
        self.loading_progress = 0
        self.user_sessions = {}
        
        print(f"🚀 TTS 웹 서비스 초기화 - 디바이스: {self.device}")
        
        # torch.load 패치 (Mac용)
        self.setup_torch_patch()
        
        # 모델 로딩 시작
        self.load_model_async()
    
    def setup_torch_patch(self):
        """Mac M1/M2/M3/M4 최적화를 위한 torch.load 패치"""
        map_location = torch.device(self.device)
        torch_load_original = torch.load
        def patched_torch_load(*args, **kwargs):
            if 'map_location' not in kwargs:
                kwargs['map_location'] = map_location
            return torch_load_original(*args, **kwargs)
        torch.load = patched_torch_load
        print("✅ torch.load 패치 완료")
    
    def load_model_async(self):
        """비동기로 모델 로딩"""
        def load():
            try:
                self.is_loading = True
                self.loading_progress = 10
                print("📥 다국어 TTS 모델을 로드하는 중...")
                
                self.model = ChatterboxMultilingualTTS.from_pretrained(device=self.device)
                
                self.loading_progress = 100
                self.is_loading = False
                print("✅ 모델 로딩 완료!")
                
            except Exception as e:
                print(f"❌ 모델 로딩 실패: {e}")
                self.is_loading = False
                self.loading_progress = 0
        
        threading.Thread(target=load, daemon=True).start()
    
    def is_ready(self):
        """모델이 준비되었는지 확인"""
        return self.model is not None and not self.is_loading
    
    def get_loading_status(self):
        """로딩 상태 반환"""
        return {
            "is_loading": self.is_loading,
            "progress": self.loading_progress,
            "is_ready": self.is_ready()
        }
    
    def generate_tts(self, text, emotion="neutral", speed=1.0, exaggeration=1.0, cfg_weight=0.5, user_id=None):
        """TTS 생성"""
        if not self.is_ready():
            raise Exception("모델이 아직 로딩되지 않았습니다.")
        
        try:
            print(f"🎵 TTS 생성 시작: {text[:50]}...")
            
            # 감정에 따른 설정 조정
            if emotion == "happy":
                exaggeration = min(1.5, exaggeration + 0.3)
            elif emotion == "sad":
                exaggeration = max(0.7, exaggeration - 0.2)
            elif emotion == "angry":
                exaggeration = min(1.8, exaggeration + 0.4)
            elif emotion == "excited":
                exaggeration = min(1.6, exaggeration + 0.3)
            elif emotion == "calm":
                exaggeration = max(0.6, exaggeration - 0.3)
            
            # 음성 생성
            wav = self.model.generate(
                text,
                language_id="ko",
                exaggeration=exaggeration,
                cfg_weight=cfg_weight
            )
            
            # 파일명 생성 (사용자별 폴더)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if user_id:
                user_dir = os.path.join("generated_audio", user_id)
                os.makedirs(user_dir, exist_ok=True)
                filename = f"tts_{emotion}_{timestamp}.wav"
                filepath = os.path.join(user_dir, filename)
            else:
                filename = f"tts_{emotion}_{timestamp}.wav"
                filepath = os.path.join("generated_audio", filename)
            
            # 오디오 파일 저장
            os.makedirs("generated_audio", exist_ok=True)
            ta.save(filepath, wav, self.model.sr)
            
            print(f"✅ TTS 생성 완료: {filename}")
            
            return {
                "success": True,
                "audioFile": filename,
                "filePath": filepath,
                "duration": len(wav) / self.model.sr,
                "sampleRate": self.model.sr,
                "userId": user_id
            }
            
        except Exception as e:
            print(f"❌ TTS 생성 실패: {e}")
            raise e

# TTS 서비스 인스턴스 생성
tts_service = TTSWebService()

@app.route('/')
def index():
    """메인 페이지"""
    return render_template('index.html')

@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    status = tts_service.get_loading_status()
    return jsonify({
        "status": "running",
        "device": tts_service.device,
        "model_ready": status["is_ready"],
        "model_loading": status["is_loading"],
        "loading_progress": status["progress"]
    })

@app.route('/api/status', methods=['GET'])
def get_status():
    """모델 로딩 상태 확인"""
    return jsonify(tts_service.get_loading_status())

@app.route('/api/generate', methods=['POST'])
def generate_tts():
    """TTS 생성 API"""
    try:
        data = request.get_json()
        
        # 필수 필드 확인
        required_fields = ['text']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "success": False,
                    "error": f"필수 필드 '{field}'가 없습니다."
                }), 400
        
        # 기본값 설정
        text = data['text']
        emotion = data.get('emotion', 'neutral')
        speed = data.get('speed', 1.0)
        exaggeration = data.get('exaggeration', 1.0)
        cfg_weight = data.get('cfgWeight', 0.5)
        
        # 텍스트 길이 확인
        if len(text) > 500:
            return jsonify({
                "success": False,
                "error": "텍스트가 너무 깁니다. (최대 500자)"
            }), 400
        
        if len(text.strip()) == 0:
            return jsonify({
                "success": False,
                "error": "텍스트를 입력해주세요."
            }), 400
        
        # 사용자 ID 생성 (세션 기반)
        user_id = session.get('user_id')
        if not user_id:
            user_id = str(uuid.uuid4())
            session['user_id'] = user_id
        
        # TTS 생성
        result = tts_service.generate_tts(
            text=text,
            emotion=emotion,
            speed=speed,
            exaggeration=exaggeration,
            cfg_weight=cfg_weight,
            user_id=user_id
        )
        
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ API 오류: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/audio/<user_id>/<filename>')
def serve_audio(user_id, filename):
    """오디오 파일 제공"""
    try:
        filepath = os.path.join("generated_audio", user_id, filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=False)
        else:
            return jsonify({"error": "파일을 찾을 수 없습니다."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/audio/<filename>')
def serve_audio_legacy(filename):
    """레거시 오디오 파일 제공"""
    try:
        filepath = os.path.join("generated_audio", filename)
        if os.path.exists(filepath):
            return send_file(filepath, as_attachment=False)
        else:
            return jsonify({"error": "파일을 찾을 수 없습니다."}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/list-audio', methods=['GET'])
def list_audio():
    """생성된 오디오 파일 목록"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"files": []})
        
        audio_dir = os.path.join("generated_audio", user_id)
        if not os.path.exists(audio_dir):
            return jsonify({"files": []})
        
        files = []
        for filename in os.listdir(audio_dir):
            if filename.endswith('.wav'):
                filepath = os.path.join(audio_dir, filename)
                stat = os.stat(filepath)
                files.append({
                    "filename": filename,
                    "size": stat.st_size,
                    "created": stat.st_ctime
                })
        
        # 생성 시간순으로 정렬
        files.sort(key=lambda x: x["created"], reverse=True)
        return jsonify({"files": files})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/cleanup', methods=['POST'])
def cleanup_audio():
    """오래된 오디오 파일 정리"""
    try:
        data = request.get_json()
        max_files = data.get('max_files', 10)  # 기본 10개 파일만 유지
        
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"message": "사용자 세션이 없습니다."})
        
        audio_dir = os.path.join("generated_audio", user_id)
        if not os.path.exists(audio_dir):
            return jsonify({"message": "정리할 파일이 없습니다."})
        
        files = []
        for filename in os.listdir(audio_dir):
            if filename.endswith('.wav'):
                filepath = os.path.join(audio_dir, filename)
                stat = os.stat(filepath)
                files.append((filename, stat.st_ctime))
        
        # 생성 시간순으로 정렬
        files.sort(key=lambda x: x[1], reverse=True)
        
        # 오래된 파일 삭제
        deleted_count = 0
        for filename, _ in files[max_files:]:
            filepath = os.path.join(audio_dir, filename)
            try:
                os.remove(filepath)
                deleted_count += 1
            except Exception as e:
                print(f"파일 삭제 실패 {filename}: {e}")
        
        return jsonify({
            "message": f"{deleted_count}개의 오래된 파일을 삭제했습니다.",
            "deleted_count": deleted_count
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Chatterbox TTS 웹 서비스 시작")
    print(f"📱 디바이스: {tts_service.device}")
    print("🌐 서버 주소: http://localhost:5000")
    print("📋 API 엔드포인트:")
    print("  - GET  /              : 메인 웹 페이지")
    print("  - GET  /api/health    : 서버 상태 확인")
    print("  - GET  /api/status    : 모델 로딩 상태")
    print("  - POST /api/generate  : TTS 생성")
    print("  - GET  /api/audio/<user_id>/<filename> : 오디오 파일 제공")
    print("  - GET  /api/list-audio : 오디오 파일 목록")
    print("  - POST /api/cleanup   : 오래된 파일 정리")
    print("-" * 50)
    
    # 필요한 디렉토리 생성
    os.makedirs("generated_audio", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    os.makedirs("static", exist_ok=True)
    
    # 서버 시작
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',  # 모든 IP에서 접근 가능
        port=port,
        debug=False,
        threaded=True
    )
