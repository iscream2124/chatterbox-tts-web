# Chatterbox TTS 온라인 서비스

Chatterbox TTS를 온라인에서 사용할 수 있는 웹 서비스입니다.

## 🚀 주요 기능

- ✅ **한국어 TTS**: 고품질 한국어 음성 합성
- ✅ **감정 조절**: 6가지 감정 표현 (중립, 행복, 슬픔, 화남, 흥분, 차분)
- ✅ **음성 설정**: 속도, 강도, CFG 가중치 조절
- ✅ **실시간 재생**: 생성된 음성 즉시 재생
- ✅ **오디오 시각화**: 실시간 파형 표시
- ✅ **파일 다운로드**: WAV 형식으로 다운로드
- ✅ **반응형 웹**: 모바일/데스크톱 지원

## 📦 배포 방법

### 1. 로컬 실행

```bash
# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python app.py
```

서버가 `http://localhost:5000`에서 실행됩니다.

### 2. Docker로 실행

```bash
# Docker 이미지 빌드
docker build -t chatterbox-tts .

# 컨테이너 실행
docker run -p 5000:5000 -v $(pwd)/generated_audio:/app/generated_audio chatterbox-tts
```

### 3. Docker Compose로 실행

```bash
# 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

### 4. 클라우드 배포

#### AWS EC2 배포
```bash
# EC2 인스턴스에 접속
ssh -i your-key.pem ubuntu@your-ec2-ip

# Docker 설치
sudo apt update
sudo apt install docker.io docker-compose

# 프로젝트 클론
git clone your-repository
cd web-tts-service

# 서비스 시작
sudo docker-compose up -d
```

#### Google Cloud Platform 배포
```bash
# Cloud Run으로 배포
gcloud run deploy chatterbox-tts \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2
```

#### Heroku 배포
```bash
# Heroku CLI 설치 후
heroku create your-app-name
heroku config:set FLASK_ENV=production
git push heroku main
```

## 🔧 환경 설정

### 환경 변수
```bash
export FLASK_ENV=production
export PYTHONPATH=/app
```

### 포트 설정
기본 포트: 5000
변경하려면 `app.py`의 마지막 부분을 수정하세요.

## 📊 API 엔드포인트

- `GET /` - 메인 웹 페이지
- `GET /api/health` - 서버 상태 확인
- `GET /api/status` - 모델 로딩 상태
- `POST /api/generate` - TTS 생성
- `GET /api/audio/<user_id>/<filename>` - 오디오 파일 제공
- `GET /api/list-audio` - 오디오 파일 목록
- `POST /api/cleanup` - 오래된 파일 정리

## 🛡️ 보안 고려사항

1. **Rate Limiting**: API 호출 제한 설정
2. **Authentication**: 사용자 인증 시스템 추가
3. **File Cleanup**: 정기적인 임시 파일 정리
4. **HTTPS**: SSL 인증서 설정
5. **CORS**: 적절한 CORS 정책 설정

## 📈 성능 최적화

1. **모델 캐싱**: 모델을 메모리에 유지
2. **파일 정리**: 자동 파일 정리 스케줄링
3. **로드 밸런싱**: 여러 인스턴스 실행
4. **CDN**: 정적 파일 CDN 사용

## 🔍 모니터링

### 로그 확인
```bash
# Docker 로그
docker-compose logs -f chatterbox-tts

# 시스템 로그
tail -f /var/log/syslog
```

### 헬스체크
```bash
curl http://localhost:5000/api/health
```

## 🚨 문제 해결

### 일반적인 문제들

1. **모델 로딩 실패**
   - GPU 메모리 부족 확인
   - Python 버전 호환성 확인

2. **오디오 생성 실패**
   - 디스크 공간 확인
   - 권한 문제 확인

3. **웹 페이지 로딩 실패**
   - 포트 충돌 확인
   - 방화벽 설정 확인

## 📝 라이선스

MIT License

## 🤝 기여하기

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📞 지원

문제가 있으시면 GitHub Issues에 문의해주세요.
